from flask import Flask, render_template, request  # Import necessary Flask modules to create the web app, render HTML templates, and handle HTTP requests.
import requests  # Import requests module to make HTTP requests.
import urllib3  # Import urllib3 to handle SSL warning suppression.

# Disable SSL warnings for testing purposes. This prevents warnings when using self-signed SSL certificates.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize the Flask app.
app = Flask(__name__)
app.secret_key = '\x1f\xf9K\x91E1\x7fJ\x94\xd8\xea\x1d\xe5r\xb9\xe1=p\xe5\xf8\n\xca\x88\x89'  # Secret key used for session management in Flask.

# Proxmox server details for API access.
PROXMOX_URL = "https://192.168.1.252:8006/api2/json"  # URL for Proxmox API endpoint.
TOKEN_ID = "pythonapi@pam!apipython"  # Token ID for authentication.
TOKEN_SECRET = "8b13892c-c6e9-43c0-b128-3f17dd0f932a"  # Token secret for authentication.
NODE = "innprox-02"  # Node on which the VM will be created.

# API headers to include authorization and content type.
headers = {
    'Authorization': f'PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}',  # Authorization header for Proxmox API token.
    'Content-Type': 'application/json'  # Specify JSON content type for the request body.
}

# Route for the homepage that displays the VM creation form.
@app.route('/')
def index():
    return render_template('create_vm.html')  # Render the 'create_vm.html' template.

# Route for handling VM creation form submission.
@app.route('/create_vm', methods=['POST'])
def create_vm():
    # Get data from the form submitted by the user.
    vmid = request.form['vmid']  # VM ID from the form.
    name = request.form['name']  # VM name from the form.
    memory = request.form['memory']  # Memory size in MB from the form.
    cores = request.form['cores']  # Number of CPU cores from the form.

    # Create a payload with VM configuration details.
    payload = {
        "vmid": vmid,  # VM ID to be used.
        "name": name,  # Name of the VM.
        "memory": int(memory),  # Memory size as an integer.
        "cores": int(cores),  # Number of CPU cores as an integer.
        "sockets": 1,  # Number of CPU sockets.
        "cpu": "x86-64-v2-AES",  # CPU type.
        "ostype": "l26",  # OS type (Linux).
        "scsihw": "virtio-scsi-single",  # SCSI controller type.
        "net0": "virtio,bridge=vmbr0,firewall=1",  # Network configuration.
        "ide2": "storage1:iso/ubuntu-22.04.5-desktop-amd64.iso,media=cdrom",  # Path to ISO file for installation.
        "virtio0": "storage1:32,format=qcow2,iothread=on",  # Disk configuration with storage type and size.
        "boot": "order=ide2;virtio0"  # Boot order to boot from the ISO.
    }

    # Proxmox API endpoint for creating a new VM.
    url = f"{PROXMOX_URL}/nodes/{NODE}/qemu"

    try:
        # Make a POST request to create the VM.
        response = requests.post(url, headers=headers, json=payload, verify=False)

        # Check if the request was successful.
        if response.status_code in [200, 202]:
            message = "VM creation initiated successfully!"  # Success message.
            print("VM creation initiated successfully:", response.json())  # Print response for debugging.
        else:
            # Message for a failed request, possibly due to duplicate VM ID or other errors.
            message = f"Failed to create VM and This VM ID Present on Proxmox"

    except requests.RequestException as e:
        # Handle request exceptions (e.g., network issues).
        message = f"Network issues on server"

    # Render the 'create_vm.html' template with a message indicating the result.
    return render_template('create_vm.html', message=message)

# Run the app in debug mode to show detailed error messages.
if __name__ == "__main__":
    app.run(debug=True)

















2)


from flask import Flask, render_template, request
import requests
import urllib3

# Disable SSL warnings for testing purposes
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = '\x1f\xf9K\x91E1\x7fJ\x94\xd8\xea\x1d\xe5r\xb9\xe1=p\xe5\xf8\n\xca\x88\x89'

# Proxmox server details
PROXMOX_URL = "https://192.168.1.252:8006/api2/json"
TOKEN_ID = "pythonapi@pam!apipython"
TOKEN_SECRET = "8b13892c-c6e9-43c0-b128-3f17dd0f932a"
node = 'innprox-02'

# API headers for Proxmox authorization
headers = {
    'Authorization': f'PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}',
    'Content-Type': 'application/json'
}

# Function to get the next available VM ID
def get_available_vmid(node):
    url = f"{PROXMOX_URL}/nodes/{node}/qemu"
    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            existing_vms = response.json()['data']
            existing_vmids = [vm['vmid'] for vm in existing_vms]
            vmid = 200
            while vmid in existing_vmids:
                vmid += 1
            return vmid
        else:
            raise Exception(f"Failed to fetch existing VMs. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        raise Exception(f"Error fetching VM list from Proxmox: {str(e)}")

@app.route('/')
def index():
    vmid = get_available_vmid(node)
    return render_template('create_vm.html', vmid=vmid)

@app.route('/create_vm', methods=['POST'])
def create_vm():
    name = request.form['name']
    memory = request.form['memory']
    cores = request.form['cores']
    storage_size = request.form['storage_size']

    vmid = get_available_vmid(node)

    # Create the payload for VM configuration
    payload = {
        "vmid": vmid,
        "name": name,
        "memory": int(memory),
        "cores": int(cores),
        "sockets": 1,
        "cpu": "x86-64-v2-AES",  # 64-bit CPU with AES support
        "ostype": "l26",  # Linux 2.6+
        "scsihw": "virtio-scsi-single",  # Virtio SCSI controller
        "net0": "virtio,bridge=vmbr0,firewall=1",  # Virtio network
        "ide2": "storage1:iso/ubuntu-24.04.1-live-server-amd64.iso,media=cdrom",  # ISO for installation
        "virtio0": f"storage1:{storage_size},format=qcow2,iothread=on",  # Storage size in qcow2 format
        "boot": "order=virtio0;ide2",  # Boot from virtual disk (virtio0) first, then ISO (ide2)
        "agent": 1,  # QEMU guest agent enabled
        "onboot": 1,  # VM starts automatically on host boot
    }

    url = f"{PROXMOX_URL}/nodes/{node}/qemu"

    try:
        # Send POST request to Proxmox API to create the VM
        response = requests.post(url, headers=headers, json=payload, verify=False)

        if response.status_code == 200:
            message = f"VM creation initiated successfully with VMID {vmid} on Node {node}!"
            return render_template('create_vm.html', message=message)
        else:
            # Detailed error handling
            error_details = response.json() if response.status_code != 200 else response.text
            message = f"Failed to create VM. Error details: {error_details}"
            return render_template('create_vm.html', message=message)

    except requests.RequestException as e:
        message = f"Error connecting to Proxmox server: {str(e)}"
        return render_template('create_vm.html', message=message)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)




3)


# Define the route for creating a VM
@app.route('/create_vm', methods=['GET', 'POST'])
def create_vm():
    # Define the get_available_vmid function
    PROXMOX_URL = "https://192.168.1.252:8006/api2/json"
    TOKEN_ID = "pythonapi@pam!apipython"
    TOKEN_SECRET = "8b13892c-c6e9-43c0-b128-3f17dd0f932a"
    node_name  = "innprox-02"
    headers = {
        'Authorization': f'PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}',
        'Content-Type': 'application/json'
    }
     # Function to start the VM
    def start_vm(vmid):
        hostname = '192.168.1.252'
        username = 'root'
        private_key_path = '/home/innuser002/.ssh/id_rsa'
        port = 22
        
        # SSH client setup
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = RSAKey.from_private_key_file(private_key_path)
        ssh_client.connect(hostname, port=port, username=username, pkey=private_key)

        # Command to start the container/VM
        stdin, stdout, stderr = ssh_client.exec_command(f'qm start {vmid}')
        result = stdout.read().decode().strip()
        error = stderr.read().decode()
        ssh_client.close()

        if error:
            raise Exception(f"Error starting VM {vmid}: {error}")

        return result

    def get_available_vmid(node):
        url = f"{PROXMOX_URL}/nodes/{node}/qemu"
        try:
            response = requests.get(url, headers=headers, verify=False)
            if response.status_code == 200:
                existing_vms = response.json()['data']
                existing_vmids = [vm['vmid'] for vm in existing_vms]
                vmid = 2008
                while vmid in existing_vmids:
                    vmid += 1
                return vmid
            else:
                raise Exception("Failed to fetch existing VMs.")
        except requests.RequestException as e:
            raise Exception(f"Error fetching VM list from Proxmox: {str(e)}")

    # Get the file_name parameter from the query string (for both GET and POST requests)
    file_name = request.args.get('file_name')
    print(f"Requested file: {file_name}")

    # Check if the file exists at the specified location
    file_path = f"/home/nfs_client/{file_name}"
    if not os.path.exists(file_path):
        message = f"File '{file_name}' does not exist at the specified location."
        return render_template('create_vm.html', message=message)

    # Proceed with the VM creation if file exists
    vmid = get_available_vmid(node_name)  # Fetch VMID once for both GET and POST requests

    if request.method == 'POST':
        # Handle POST request for creating a VM
        name = request.form['name']  # VM name
        
        # Create the clone payload with dynamic vmid
        clone_payload = {
            "newid": vmid,  # The ID for the new VM
            "name": name,  # The name for the new VM
            "full": 1,  # Perform a full clone
            "storage": "storage1",  # Storage where the cloned disk will be created (adjust to your setup)
        }

        url = f"{PROXMOX_URL}/nodes/{node_name}/qemu/{file_name}/clone"
        try:
            response = requests.post(url, headers=headers, json=clone_payload, verify=False)
            if response.status_code in [200, 202]:
                message = "VM creation initiated successfully from the template!"  
                 # Start the VM automatically after creation
                try:
                    start_vm(vmid)
                    message += " The VM has been started automatically."
                except Exception as e:
                    message += f" However, there was an error starting the VM: {str(e)}"
            else:
                message = f"Failed to clone VM: {response.text}"
        except requests.RequestException as e:
            message = f"Network issues: {str(e)}"

        return render_template('create_vm.html', message=message, vmid=vmid)

    # For GET request, render the form with vmid and file_name
    return render_template('create_vm.html', vmid=vmid, file_name=file_name)




