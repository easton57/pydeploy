import csv
import sys
import winrm
import subprocess

from os import listdir, mkdir
from getpass import getpass

# TODO: Create logging


def cli_run():
    # Declare empty list
    computers = []

    # CSV column name for patches
    csv_field = input("Enter the csv column name for your computers: ")

    # List of target Windows hosts from csv
    with open ('computers.csv', mode='r') as comp_file:
        read_csv = csv.DictReader(comp_file)
        for i in read_csv:
            computers.append(i[csv_field])

    # Read list of patches in patch directory
    patch_names = listdir('patches')

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


def deploy_software(username, password, patch_name, computers):
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

        # Establish a connection to the remote Windows machine
        session = winrm.Session(f"{computer}", auth=(username, password), transport='ntlm')
        
        if 'msi' in patch_name:
            if 'oledb' in patch_name:
                additional_args = "IACCEPTMSOLEDBSQLLICENSETERMS=YES"
            elif 'odbc' in patch_name:
                additional_args = "IACCEPTMSODBCSQLLICENSETERMS=YES"
            else:
                additional_args = ""

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
        
        # Execute the PowerShell script on the remote machine
        result = session.run_ps(script)
        
        if result.status_code == 0:
            print(f"Successfully installed {patch_name} on {computer}")
        else:
            print(f"Failed to install {patch_name} on {computer}")

        # Clear patches folder from remote host
        process=subprocess.Popen(["powershell", f"Remove-Item {patch_dir} -recurse"], stdout=subprocess.PIPE)
        process.communicate()

def folder_check(folder_name):
    if folder_name not in listdir('.'):
        print(f"Created {folder_name} folder")
        mkdir(folder_name)
    else:
        print(f"{folder_name} folder exists... continuing...\n\n")

if __name__ == "__main__":
    # Create needed directories
    folder_check('patches')
    folder_check('logs')
    
    # Run the CLI
    # TODO: Create a GUI
    cli_run()
