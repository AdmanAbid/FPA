import math

EXP_BITS = 4
FRAC_BITS = 11
EXP_BIAS = 7
GUARD_BITS = 8

EXP_ALL_ONES = (1 << EXP_BITS) - 1      # 15
EXP_MAX_NORMAL = EXP_ALL_ONES - 1       # 14
FRAC_MAX = (1 << FRAC_BITS) - 1

SIGN_BIT = 15
EXP_START = FRAC_BITS
FRAC_START = 0


def bit_extract(value, start, width):
    return (value >> start) & ((1 << width) - 1)

def bit_set(value, start, width, bits):
    mask = ((1 << width) - 1) << start
    return (value & ~mask) | ((bits << start) & mask)

def construct_float(sign, exp, frac):
    x = 0
    x = bit_set(x, SIGN_BIT, 1, sign)
    x = bit_set(x, EXP_START, EXP_BITS, exp)
    x = bit_set(x, FRAC_START, FRAC_BITS, frac)
    return x & 0xFFFF


class SEF:
    def __init__(self, sign: int, exponent: int, fraction: int):
        self.sign = sign & 1
        self.exponent = exponent & EXP_ALL_ONES
        self.fraction = fraction & FRAC_MAX

    def to_float(self) -> float:
        if self.exponent == 0:
            if self.fraction == 0:
                return -0.0 if self.sign else 0.0
            exponent_value = 1 - EXP_BIAS
            fraction_value = self.fraction / (1 << FRAC_BITS)
            return (-1.0 if self.sign else 1.0) * fraction_value * (2 ** exponent_value)

        if self.exponent == EXP_ALL_ONES:
            if self.fraction == 0:
                return float("-inf") if self.sign else float("inf")
            return float("nan")

        exponent_value = self.exponent - EXP_BIAS
        fraction_value = self.fraction / (1 << FRAC_BITS)
        return (-1.0 if self.sign else 1.0) * (1 + fraction_value) * (2 ** exponent_value)

    def to_binary_string(self) -> str:
        return f"{self.sign:1b}{self.exponent:0{EXP_BITS}b}{self.fraction:0{FRAC_BITS}b}"

    @classmethod
    def from_binary_string(cls, bits: str):
        clean = "".join(ch for ch in bits if ch in "01")
        if len(clean) != 1 + EXP_BITS + FRAC_BITS:
            raise ValueError("SEF binary string must be 16 bits long")
        sign = int(clean[0], 2)
        exponent = int(clean[1:1 + EXP_BITS], 2)
        fraction = int(clean[1 + EXP_BITS:], 2)
        return cls(sign, exponent, fraction)

    @classmethod
    def from_float(cls, value: float):
        if math.isnan(value):
            return cls(0, EXP_ALL_ONES, 1)
        if math.isinf(value):
            return cls(1 if value < 0 else 0, EXP_ALL_ONES, 0)
        if value == 0.0:
            return cls(1 if math.copysign(1.0, value) < 0 else 0, 0, 0)

        sign = 1 if value < 0 else 0
        value = abs(value)

        mantissa, exponent = math.frexp(value)
        mantissa *= 2.0
        exponent -= 1

        exp_bits = exponent + EXP_BIAS
        if exp_bits <= 0:
            exponent_bits = 0
            scaled = value / (2 ** (1 - EXP_BIAS))
            fraction = int(round(scaled * (1 << FRAC_BITS)))
            fraction = min(max(fraction, 0), FRAC_MAX)
            if fraction == 0:
                return cls(sign, 0, 0)
            return cls(sign, exponent_bits, fraction)

        if exp_bits >= EXP_ALL_ONES:
            return cls(sign, EXP_ALL_ONES, 0)

        fraction = int(round((mantissa - 1.0) * (1 << FRAC_BITS)))
        if fraction > FRAC_MAX:
            fraction = 0
            exp_bits += 1
            if exp_bits >= EXP_ALL_ONES:
                return cls(sign, EXP_ALL_ONES, 0)

        return cls(sign, exp_bits, fraction)


def floating_point_adder(a, b):
    sa = bit_extract(a, SIGN_BIT, 1)
    ea = bit_extract(a, EXP_START, EXP_BITS)
    fa = bit_extract(a, FRAC_START, FRAC_BITS)

    sb = bit_extract(b, SIGN_BIT, 1)
    eb = bit_extract(b, EXP_START, EXP_BITS)
    fb = bit_extract(b, FRAC_START, FRAC_BITS)

    # ---- NaN handling
    if ea == EXP_ALL_ONES and fa != 0:
        return construct_float(0, EXP_ALL_ONES, 1)
    if eb == EXP_ALL_ONES and fb != 0:
        return construct_float(0, EXP_ALL_ONES, 1)

    # ---- Infinity
    if ea == EXP_ALL_ONES:
        if eb == EXP_ALL_ONES and sa != sb:
            return construct_float(0, EXP_ALL_ONES, 1)
        return a
    if eb == EXP_ALL_ONES:
        return b

    # ---- Zero
    if ea == 0 and fa == 0:
        return b
    if eb == 0 and fb == 0:
        return a

    # ---- Build mantissas
    ma = fa | (1 << FRAC_BITS) if ea != 0 else fa
    mb = fb | (1 << FRAC_BITS) if eb != 0 else fb

    ea = ea if ea != 0 else 1
    eb = eb if eb != 0 else 1

    # ---- Align exponents with proper rounding
    # Use more guard bits (8) to maintain precision during alignment

    ma <<= GUARD_BITS
    mb <<= GUARD_BITS
    
    if ea > eb:
        shift = ea - eb
        if shift > 0 and shift < 64:
            # Capture all bits that will be shifted out as sticky
            sticky_mask = (1 << shift) - 1
            sticky_bits = mb & sticky_mask
            mb >>= shift
            # OR in sticky bit if any bits were shifted out
            if sticky_bits != 0:
                mb |= 1
        elif shift >= 64:
            mb = 1 if mb != 0 else 0
        exp = ea
    else:
        shift = eb - ea
        if shift > 0 and shift < 64:
            # Capture all bits that will be shifted out as sticky
            sticky_mask = (1 << shift) - 1
            sticky_bits = ma & sticky_mask
            ma >>= shift
            # OR in sticky bit if any bits were shifted out
            if sticky_bits != 0:
                ma |= 1
        elif shift >= 64:
            ma = 1 if ma != 0 else 0
        exp = eb

    # ---- Add / subtract
    if sa == sb:
        mant = ma + mb
        sign = sa
    else:
        if ma >= mb:
            mant = ma - mb
            sign = sa
        else:
            mant = mb - ma
            sign = sb

    # ---- Cancellation
    # if mant == 0:
    #     return construct_float(0, 0, 0)

    # ---- Normalize (mant has GUARD_BITS extra LSBs for rounding)
    target_bit = FRAC_BITS + GUARD_BITS  # Position of implicit bit with guard bits
    while mant >= (1 << (target_bit + 1)):
        # Capture sticky bit when shifting right
        sticky = mant & 1
        mant = (mant >> 1) | sticky
        exp += 1

    while mant < (1 << target_bit) and exp > 1:
        mant <<= 1
        exp -= 1

    # ---- Round to nearest, ties to even
    # Extract GRS bits: we keep bottom 3 bits as Guard, Round, Sticky
    # and need to compress the extra GUARD_BITS down to 3
    guard_mask = (1 << GUARD_BITS) - 1
    all_guard_bits = mant & guard_mask
    mant >>= GUARD_BITS
    
    # Now extract the actual GRS from the remaining mantissa
    guard = (all_guard_bits >> (GUARD_BITS - 1)) & 1
    round_bit = (all_guard_bits >> (GUARD_BITS - 2)) & 1
    sticky_bits = all_guard_bits & ((1 << (GUARD_BITS - 2)) - 1)
    sticky = 1 if sticky_bits != 0 else 0
    lsb = mant & 1
    
    # Round up if: guard is set AND (round OR sticky OR (guard AND lsb for ties))
    round_up = guard and (round_bit or sticky or lsb)
    
    if round_up:
        mant += 1
        # Check for overflow after rounding
        if mant >= (1 << (FRAC_BITS + 1)):
            mant >>= 1
            exp += 1


    # ---- Cancellation
    if mant == 0:
        return construct_float(sign, 0, 0)

    # ---- Overflow
    if exp >= EXP_ALL_ONES:
        return construct_float(sign, EXP_ALL_ONES, 0)

    # ---- Gradual underflow
    ### simplification from : exp <= 0
    if exp == 0: 
        mant >>= (1 - exp)
        return construct_float(sign, 0, mant & FRAC_MAX)

    # ---- Result is subnormal (couldn't normalize to >= 2048 because exp=1)
    ### simplification from : exp == 1 and mant < (1 << FRAC_BITS)
    if mant < (1 << FRAC_BITS):
        return construct_float(sign, 0, mant & FRAC_MAX)

    # ---- Normal result
    frac = mant & FRAC_MAX
    return construct_float(sign, exp, frac)
