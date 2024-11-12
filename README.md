Developed a Python Flask app to access the Proxmox API. This app utilizes an API key and secret key to interact with the Proxmox API.
Created functionality in the Python Flask app to send requests to the Proxmox API for the creation of new virtual machines(VM) with specified configurations.
Implemented a validation check where, if the VM ID is already present, a message stating "VM is already there" is displayed. Otherwise, a message indicating "VM created successfully" is shown.

Run:
python3 python_flask_vm.py
