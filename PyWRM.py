import winrm
import getpass as getpass

# List of target Windows hosts from csv
computers = ("host1", "host2", "host3")

# Patch Directory
patch_dir = "\\\\Some\\Path\\To\\Patches\\"

# Read list of patches in patch directory
patch_names = ('stuff')

num = 0

for i in patch_names:
    print(f"{num}: {i}")
    num += 1

patch_select = input("Select a patch number to install: ")

patch_name = patch_names[patch_select]

# Get username and password
username = input("Enter username: ")
password = getpass("Enter password: ")

for computer in computers:
    # Establish a connection to the remote Windows machine
    session = winrm.Session(computer, auth=('username', 'password'))
    
    # PowerShell script to install software patches from the shared path or URL
    script = f"""
    Start-Process msiexec.exe -Wait -ArgumentList "/i {patch_dir}{patch_name} /qn"
    """
    
    # Execute the PowerShell script on the remote machine
    result = session.run_ps(script)
    
    if result.status_code == 0:
        print(f"Successfully installed software patch on {computer}")
    else:
        print(f"Failed to install software patch on {computer}")
