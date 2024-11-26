import csv
import sys
import winrm
import subprocess

from os import listdir, mkdir
from getpass import getpass

import winrm.exceptions

# TODO: Create logging


def cli_run():
    # Health check
    health_check()

    # CSV column name for patches
    csv_field = input("Enter the csv column name for your computers: ")

    # List of target Windows hosts from csv
    computers = get_computers("computers.csv", csv_field)

    # Read list of patches in patch directory
    patch_names = read_patches()

    num = 0

    for i in patch_names:
        print(f"{num}: {i}")
        num += 1

    patch_select = int(input("Select a patch number to install: "))

    patch_name = patch_names[patch_select]

    # Get username and password
    username = input("Enter username: ")
    password = getpass("Enter password: ")

    # Send it to the deployment software
    deploy_software(username, password, patch_name, computers)


def deploy_software(username, password, patch_name, computers, additional_args):
    # Loop through the read computers
    for computer in computers:
        # Patch Directory
        patch_dir = f"\\\\{computer}\\c$\\Patches\\"

        # Create patch path on remote server
        process=subprocess.Popen(["powershell", f"mkdir {patch_dir}"], stdout=subprocess.PIPE)
        process.communicate()

        # Copy patch to remote server
        process=subprocess.Popen(["powershell", f"Copy-Item -Path patches\\{patch_name} -Destination {patch_dir}"], stdout=subprocess.PIPE)
        process.communicate()

        # Copy the permissions file if needed
        if 'perms' in patch_name:
            # Copy perms file to remote server
            process=subprocess.Popen(["powershell", f"Copy-Item -Path patches\\perms.txt -Destination {patch_dir}"], stdout=subprocess.PIPE)
            process.communicate()

        # Establish a connection to the remote Windows machine
        session = winrm.Session(f"{computer}", auth=(username, password), transport='ntlm')
        
        if 'msi' in patch_name:
            if 'oledb' in patch_name:
                additional_args = "IACCEPTMSOLEDBSQLLICENSETERMS=YES"
            elif 'odbc' in patch_name:
                additional_args = "IACCEPTMSODBCSQLLICENSETERMS=YES"

            # PowerShell script to install software patches from the shared path or URL
            script = f"""
            msiexec /i {patch_dir}{patch_name} /qn {additional_args}
            """
        elif 'azuredatastudio' in patch_name:
            script = f"""
            {patch_dir}{patch_name} /VERYSILENT /MERGETASKS=!runcode
            """
        elif 'ps1' in patch_name:
            script = f"""
            powershell {patch_dir}{patch_name}
            """
        else:  # Default for EXE
            script = f"""
            start-process -FilePath "{patch_dir}{patch_name}" -ArgumentList '/S' -Verb runas -Wait
            """  # This may only work on notepad++ but we will see later.
        
        try:
            # Execute the PowerShell script on the remote machine
            result = session.run_ps(script)

            if result.status_code == 0:
                print(f"Successfully installed {patch_name} on {computer}")
            else:
                print(f"Failed to install {patch_name} on {computer}")

            # Clear patches folder from remote host
            process=subprocess.Popen(["powershell", f"Remove-Item {patch_dir} -recurse"], stdout=subprocess.PIPE)
            process.communicate()
        except winrm.exceptions.InvalidCredentialsError:
            print(f"Invalid Credentials! Check your password or permissions on the remote system {computer}.")

def health_check():
    # Create needed directories
    folder_check('patches')
    folder_check('logs')

def folder_check(folder_name):
    if folder_name not in listdir('.'):
        print(f"Created {folder_name} folder")
        mkdir(folder_name)
    else:
        print(f"{folder_name} folder exists... continuing...\n")

def get_computers(csv_file, csv_field) -> list:
    """Return the list of computers from the specified CSV file"""
    computers = []

    with open (csv_file, mode='r') as comp_file:
        read_csv = csv.DictReader(comp_file)
        for i in read_csv:
            computers.append(i[csv_field])

    return computers

def read_patches() -> list:
    """ Modularity is cool (this is for easier reading from the GUI)"""
    return listdir('patches')

if __name__ == "__main__":
    # Run the CLI if launched directly
    cli_run()
