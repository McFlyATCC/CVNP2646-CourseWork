# indentation_demo.py
# Demonstrating correct and incorrect indentation

# CORRECT: Consistent 4-space indentation
def check_port(port):
    if port < 1024:
        print("System port - requires root privileges")
        if port == 22:
            print("SSH port detected")
    else:
        print("User port - standard privileges")

check_port(22)
check_port(8080)

# INCORRECT: This will cause IndentationError
def broken_function():
    print("First line")
print("Second line - ERROR! Wrong indentation")