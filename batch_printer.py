# AI generated cause I can't be bothered to write this shit myself

import os
import subprocess
import time


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

directory = ""
wait_seconds = 5


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


def print_file(file_path):
    """
    Use Windows Explorer's registered Print action via PowerShell.
    Equivalent to:
        Start-Process -FilePath "..." -Verb Print
    """

    # Escape single quotes for PowerShell
    ps_path = str(file_path).replace("'", "''")

    command = f"Start-Process -FilePath '{ps_path}' -Verb Print"

    subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], check=True)


def print_range():
    if not directory:
        print("\nPlease configure the target directory first.")
        input("Press Enter to continue...")
        return

    try:
        start = int(input("\nStart file number: "))
        end = int(input("End file number: "))
    except ValueError:
        print("Please enter valid numbers.")
        input("Press Enter to continue...")
        return

    if start > end:
        print("Start number must be <= end number.")
        input("Press Enter to continue...")
        return

    print()
    print(f"Directory : {directory}")
    print(f"Range     : {start} - {end}")
    print(f"Wait time : {wait_seconds} seconds")
    print()

    try:
        for number in range(start, end + 1):
            file_path = os.path.join(directory, f"output-{number}.pdf")

            if not os.path.isfile(file_path):
                print(f"[SKIP] File not found: {file_path}")
                continue

            print(f"[PRINT] output-{number}.pdf")

            print_file(file_path)

            # Don't wait after the final file
            if number < end:
                print(f"       Waiting {wait_seconds} seconds...")
                time.sleep(wait_seconds)

        print("\nPrinting completed.")
        input("Press Enter to return to the main menu...")

    except KeyboardInterrupt:
        print("\n\nPrinting interrupted.")
        print("Returning to main menu...")
        time.sleep(1)


def configure_directory():
    global directory

    new_directory = input(f"\nDirectory [{directory or 'not configured'}]: ").strip()

    if new_directory:
        new_directory = new_directory.strip('"')

        if not os.path.isdir(new_directory):
            print(f"Directory does not exist: {new_directory}")
            input("Press Enter to continue...")
            return

        directory = os.path.abspath(new_directory)

    print(f"Directory set to: {directory}")
    input("Press Enter to continue...")


def configure_wait_time():
    global wait_seconds

    try:
        value = float(input(f"\nWait time in seconds [{wait_seconds}]: "))

        if value < 0:
            raise ValueError

        wait_seconds = value

    except ValueError:
        print("Please enter a valid non-negative number.")
        input("Press Enter to continue...")
        return

    print(f"Wait time set to: {wait_seconds} seconds")
    input("Press Enter to continue...")


# ------------------------------------------------------------
# Main menu
# ------------------------------------------------------------


def main():
    while True:
        os.system("cls")

        print("=" * 50)
        print("             PDF BATCH PRINTER")
        print("=" * 50)
        print()
        print(f"Directory : {directory or 'Not configured'}")
        print(f"Wait time : {wait_seconds} seconds")
        print()
        print("1. Configure directory")
        print("2. Configure wait time")
        print("3. Print file range")
        print("4. Exit")
        print()
        print("=" * 50)

        choice = input("Select an option: ").strip()

        if choice == "1":
            configure_directory()

        elif choice == "2":
            configure_wait_time()

        elif choice == "3":
            print_range()

        elif choice == "4":
            print("\nGoodbye.")
            break

        else:
            print("\nInvalid selection.")
            time.sleep(1)


if __name__ == "__main__":
    main()
