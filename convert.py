#!C:\Users\adman\AppData\Local\Programs\Python\Python312\python.exe

from fpa import SEF
import sys


def binary_to_decimal(binary_str):
    """Convert 16-bit binary string to decimal float value."""
    sef = SEF.from_binary_string(binary_str)
    return sef.to_float()


def binary_to_hex(binary_str):
    """Convert 16-bit binary string to hexadecimal."""
    clean = "".join(ch for ch in binary_str if ch in "01")
    if len(clean) != 16:
        raise ValueError("Binary string must be 16 bits")
    return hex(int(clean, 2))


def decimal_to_binary(decimal_val):
    """Convert decimal float value to 16-bit binary string."""
    sef = SEF.from_float(float(decimal_val))
    return sef.to_binary_string()


def decimal_to_hex(decimal_val):
    """Convert decimal float value to hexadecimal."""
    binary = decimal_to_binary(decimal_val)
    return binary_to_hex(binary)


def hex_to_binary(hex_str):
    """Convert hexadecimal to 16-bit binary string."""
    # Remove 0x prefix if present
    hex_clean = hex_str.replace("0x", "").replace("0X", "")
    value = int(hex_clean, 16)
    return format(value, "016b")


def hex_to_decimal(hex_str):
    """Convert hexadecimal to decimal float value."""
    binary = hex_to_binary(hex_str)
    return binary_to_decimal(binary)


def show_all_formats(value, input_type="decimal"):
    """Display a value in all formats (binary, decimal, hex).
    
    Args:
        value: The value to convert
        input_type: One of 'binary', 'decimal', or 'hex'
    """
    if input_type == "decimal":
        dec = float(value)
        bin_str = decimal_to_binary(dec)
        hex_str = decimal_to_hex(dec)
    elif input_type == "binary":
        bin_str = value
        dec = binary_to_decimal(bin_str)
        hex_str = binary_to_hex(bin_str)
    elif input_type == "hex":
        hex_str = value
        bin_str = hex_to_binary(hex_str)
        dec = hex_to_decimal(hex_str)
    else:
        raise ValueError("input_type must be 'binary', 'decimal', or 'hex'")
    
    # Parse binary for display
    sign = bin_str[0]
    exponent = bin_str[1:5]
    fraction = bin_str[5:16]
    
    print(f"Decimal:  {dec}")
    print(f"Hex:      {hex_str}")
    print(f"Binary:   {bin_str}")
    print(f"  Sign:     {sign}")
    print(f"  Exponent: {exponent} (decimal: {int(exponent, 2)})")
    print(f"  Fraction: {fraction} (decimal: {int(fraction, 2)})")


def interactive_mode():
    """Interactive conversion tool."""
    print("16-bit Floating Point Converter")
    print("=" * 40)
    print("Commands:")
    print("  d <value>  - Convert from decimal")
    print("  b <value>  - Convert from binary (16 bits)")
    print("  h <value>  - Convert from hex")
    print("  q          - Quit")
    print()
    
    while True:
        try:
            user_input = input(">>> ").strip()
            if not user_input:
                continue
                
            if user_input.lower() == 'q':
                break
            
            parts = user_input.split(maxsplit=1)
            if len(parts) != 2:
                print("Invalid input. Use: <type> <value>")
                continue
            
            cmd, value = parts
            cmd = cmd.lower()
            
            if cmd == 'd':
                show_all_formats(value, "decimal")
            elif cmd == 'b':
                show_all_formats(value, "binary")
            elif cmd == 'h':
                show_all_formats(value, "hex")
            else:
                print(f"Unknown command: {cmd}")
            print()
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if len(sys.argv) < 3:
            print("Usage: python convert.py <d|b|h> <value>")
            sys.exit(1)
        
        value = sys.argv[2]
        
        if cmd == 'd':
            show_all_formats(value, "decimal")
        elif cmd == 'b':
            show_all_formats(value, "binary")
        elif cmd == 'h':
            show_all_formats(value, "hex")
        else:
            print("First argument must be 'd' (decimal), 'b' (binary), or 'h' (hex)")
            sys.exit(1)
    else:
        interactive_mode()