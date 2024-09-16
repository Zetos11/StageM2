import ADB
import sys
import PerfettoScan
import Const as c
import Strategy as s
import ConversionParsing as cp


def status_check(status, error_message):
    if status != 0:
        print("Status code : " + str(status) + " : " + error_message)
        exit(1)


def cleanup():
    print("Archiving previous analyses result...\n")
    f1 = open("out/archive.txt", 'w')  # use a+ to save everything
    f2 = open("out/out.txt", 'r')

    f1.write(f2.read())
    f1.close()
    f2.close()
    print("Archiving complete in archive.txt" + c.jump_line)

    print("Cleaning up previous analyses result...\n")
    open("out/out.proto", 'wb').close()
    open("out/out.txt", 'w').close()
    print("Cleanup complete" + c.jump_line)


def print_usage():
    print("Usage: python3 main.py strategy parameter(optional)\n"
          "This app can be used to retrieve energy consumption data from a connected device\n"
          "The energy consumption can be for the whole device or more specific for an app/library\n"
          "The strategy parameter can be either 'device' or 'app'\n"
          "Example: python3 main.py app maps -> will propose you app linked to a map service like google maps to monitor\n"
          "To work with TPLs you can use the following keywords: crashreporting, ads, monitoring as the parameter which will automatically start the TPL reporting\n")


def main(params):
    status = 0
    error_message = ""

    if len(params) == 0:
        print_usage()
        sys.exit(0)

    if not (params[0] == "device" or params[0] == "app"):
        print_usage()
        sys.exit(0)

    if "help" in params or "-h" in params or "--help" in params:
        print_usage()
        sys.exit(0)

    print("Welcome" + c.jump_line)

    print("Checking for connected devices...\n")
    devices = ADB.adb_devices()
    if devices == -1:
        status = -1
        error_message = "No device connected, connect a device and try again" + c.jump_line
    elif devices == 1:
        status = 1
        error_message = "More than one device connected, disconnect all devices except one and try again" + c.jump_line
    status_check(status, error_message)
    print("Device connected successfully" + c.jump_line)

    prv = PerfettoScan.power_rails_verification()
    if prv == -2:
        status = 2
        error_message = "Error while pushing config file, check if the config file name is 'verification.cfg'" + c.jump_line
    elif prv == -3:
        status = 3
        error_message = "Error while converting out.proto to out.txt, check if the input and output files names are correct" + c.jump_line
    elif prv == -4:
        status = 4
        error_message = "Your device does not support detailed Power Rails Metrics" + c.jump_line
    else:
        status = 0
        print("Your device supports detailed Power Rails Metrics" + c.jump_line)
    status_check(status, error_message)

    cleanup()

    # Checking parameters
    if len(params) == 1:
        if params[0] == "device":
            s.strategy_device()
        elif params[0] == "app":
            apps = ADB.adb_apps("")
            idx = 0
            choice = True
            print("The available apps on the device with the word '" + params[0] + "' are : ")
            if len(apps[0]) == 0:
                print("No apps found, exiting...")
                exit(0)
            for elt in apps[0]:
                if elt != "":
                    print(str(idx) + " : " + elt)
                    idx += 1
            print("\nSelect the app you want to analyze by entering the associated number or exit to quit: ")

            while choice:
                try:
                    val = input()
                    val = int(val)
                    if val < 0 or val >= len(apps[0]):
                        print("Invalid input, please enter a valid number or exit to quit 1")
                    else:
                        choice = False
                except ValueError:
                    if val == "exit":
                        print("Exiting...")
                        exit(0)
                    else:
                        print("Invalid input, please enter a valid number or exit to quit 2")

            print("You have selected: " + apps[0][val] + c.jump_line)

            s.strategy_app(apps[0][val], )

    elif len(params) == 2:
        if params[0] == "app":
            if params[1] == "crashreporting" or params[1] == "ads" or params[1] == "monitoring":
                s.strategy_tpl(params[1])
            else:
                apps = ADB.adb_apps(params[1])
                idx = 0
                choice = True
                print("The available apps on the device with the word '" + params[0] + "' are : ")
                if len(apps[0]) == 0:
                    print("No apps found, exiting...")
                    exit(0)
                for elt in apps[0]:
                    if elt != "":
                        print(str(idx) + " : " + elt)
                        idx += 1
                print("\nSelect the app you want to analyze by entering the associated number or exit to quit: ")

                while choice:
                    try:
                        val = input()
                        val = int(val)
                        if val < 0 or val >= len(apps[0]):
                            print("Invalid input, please enter a valid number or exit to quit")
                        else:
                            choice = False
                    except ValueError:
                        if val == "exit":
                            print("Exiting...")
                            exit(0)
                        else:
                            print("Invalid input, please enter a valid number or exit to quit")

                print("You have selected: " + apps[0][val] + c.jump_line)

                s.strategy_app(apps[0][val])

        else:
            print_usage()
            sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
