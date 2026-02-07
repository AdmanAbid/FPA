from fpa import *
from convert import *

def test_sample_ieee(val_a, val_b):
    # Convert inputs to custom fp16
    a_bits_str = SEF.from_float(val_a).to_binary_string()
    b_bits_str = SEF.from_float(val_b).to_binary_string()

    a_bits = int(a_bits_str, 2)
    b_bits = int(b_bits_str, 2)

    # Run IEEE-style fp16 adder
    result_bits = floating_point_adder(a_bits, b_bits)
    result_bits_str = format(result_bits, "016b")

    # Convert result back to float
    result_float = SEF.from_binary_string(result_bits_str).to_float()

    # Reference result: round *after* exact addition
    expected_float = SEF.from_float(val_a + val_b).to_float()

    pa = a_bits_str[:1] + ' ' + a_bits_str[1:5] + ' ' + a_bits_str[5:]
    pb = b_bits_str[:1] + ' ' + b_bits_str[1:5] + ' ' + b_bits_str[5:]
    pr = result_bits_str[:1] + ' ' + result_bits_str[1:5] + ' ' + result_bits_str[5:]

    print(f"{val_a} + {val_b}")
    print(f"  A bits:      {pa}  {decimal_to_hex(val_a)}")
    print(f"  B bits:      {pb}  {decimal_to_hex(val_b)}")
    print(f"  Result bits: {pr}  {binary_to_hex(result_bits_str)}")
    print(f"  Computed:    {result_float:.12g}")
    print(f"  Expected:    {expected_float:.12g}")
    print(f"  Match:       {result_float == expected_float}")
    print()


def test_floating_point_adderer_ieee():
    print("=== IEEE-style FP16 Adder Test ===\n")

    test_cases = [
        # normal numbers
        (1.5, 2.5),
        (0.5, 0.5),
        (1.0, 1.0),
        (3.5, -1.5),
        (1.0, -1.0),
        (2.0, 3.0),

        #ordering
        (1.75, -1.5),
        (-1.5, 1.75),

        # zero handling
        (0.0, 5.0),
        (-0.0, 0.0),

        # subnormal edge
        (2**-13, 2**-13),
        (2**-14, 2**-14),

        # rounding stress
        (1.00048828125, 2**-11),  # halfway case
        (1.99951171875, 2**-11),

        # cancellation
        (24.0, -24.0),
        
		#NaN
        (5000, -5000),
    ]

    for a, b in test_cases:
        test_sample_ieee(a, b)


if __name__ == "__main__":
    test_floating_point_adderer_ieee()