import os

def show_structure(root_dir="."):
    for root, dirs, files in os.walk(root_dir):
        level = root.replace(root_dir, "").count(os.sep)
        indent = "    " * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = "    " * (level + 1)
        for f in files:
            print(f"{sub_indent}{f}")

# Exemplu de rulare
if __name__ == "__main__":
    show_structure(".")
