#!/bin/bash

# Config file path
CONFIG_FILE="./config.txt"

# Default values (will be overwritten if found in the config file)
PYTHON_PATH=""
VENV_DIR=""

# Base configuration directory
BASE_CONFIG_DIR="./CONFIGS"

# Load stored config (if it exists)
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        echo "Loading stored configuration..."
        while IFS="=" read -r key value; do
            if [ "$key" == "PYTHON_PATH" ]; then
                PYTHON_PATH=$value
            elif [ "$key" == "VENV_DIR" ]; then
                VENV_DIR=$value
            fi
        done < "$CONFIG_FILE"
    fi
}

# Save configuration to config file
save_config() {
    echo "PYTHON_PATH=$PYTHON_PATH" > "$CONFIG_FILE"
    echo "VENV_DIR=$VENV_DIR" >> "$CONFIG_FILE"
    echo "Configuration saved."
}

# Automatically find Python path if not set
find_python_path() {
    if [ -z "$PYTHON_PATH" ]; then
        PYTHON_PATH=$(which python3)
        if [ -z "$PYTHON_PATH" ]; then
            echo "Python3 not found. Please install Python 3 or specify the path manually."
            exit 1
        fi
        echo "Python path automatically set to: $PYTHON_PATH"
    fi
}

# Ask for virtual environment directory if not already configured
ask_for_config() {
    find_python_path  # Automatically find Python path

    if [ -z "$VENV_DIR" ]; then
        read -p "Enter the directory where you'd like to create the virtual environment: " VENV_DIR
    fi

    save_config
}

# Function to activate the virtual environment
activate_venv() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source "$VENV_DIR/Scripts/activate"
    else
        source "$VENV_DIR/bin/activate"
    fi
}

# Check and install rshell and create virtual environment if not already done
check_rshell() {
    if ! command -v rshell &> /dev/null; then
        echo "rshell not found."
        if [ ! -d "$VENV_DIR" ]; then
            echo "Creating virtual environment in $VENV_DIR..."
            $PYTHON_PATH -m venv "$VENV_DIR"
        fi
        echo "Activating virtual environment..."
        activate_venv
        echo "Installing rshell..."
        pip install rshell
        if [ $? -ne 0 ]; then
            echo "Failed to install rshell."
            exit 1
        fi
        echo "rshell has been installed."
        save_config
    else
        echo "rshell is already installed."
    fi
}

# Prompt user for email and broker password
get_input() {
    local prompt="$1"
    read -p "$prompt: " input
    echo "$input"
}

# Function to copy files to the MicroPython device
copy_files() {
    local port=$1
    local config_dir=$2
    if [ -d "$config_dir" ]; then
        echo "Copying files to device at ${port} with config ${config_dir}..."
        rshell -p ${port} << EOF
        mkdir /pyboard/CONFIG
        mkdir /pyboard/src
        mkdir /pyboard/sao
        mkdir /pyboard/lib

        cp --recursive ${config_dir}/* /pyboard/CONFIG
        cp --recursive CONFIG/*.py /pyboard/CONFIG
        cp --recursive src/* /pyboard/src
        cp --recursive sao/* /pyboard/sao
        cp --recursive lib/* /pyboard/lib
        cp --recursive *.py /pyboard/
EOF
        
        echo "Files copied to device at ${port}."
    else
        echo "Configuration directory ${config_dir} not found. Exiting..."
        exit 1
    fi
}

# Load config
load_config
ask_for_config
check_rshell
activate_venv

# Main loop to monitor for new devices
previous_ports=($(ls /dev/ttyUSB* /dev/tty.usbmodem* /dev/cu.* 2>/dev/null || ls /dev/ttyUSB* /dev/tty.usbmodem* /dev/cu.* 2>/dev/null))

while true; do
    # Get the list of current ports for Linux, macOS, and Windows (if WSL with USB passthrough)
    current_ports=($(ls /dev/ttyUSB* /dev/tty.usbmodem* /dev/cu.* 2>/dev/null || ls /dev/ttyUSB* /dev/tty.usbmodem* /dev/cu.* 2>/dev/null))

    # Find new ports by comparing with previous state
    new_ports=($(comm -13 <(printf '%s\n' "${previous_ports[@]}" | sort) <(printf '%s\n' "${current_ports[@]}" | sort)))
    
    if [ ${#new_ports[@]} -gt 0 ]; then
        # Process each new port detected
        for port in "${new_ports[@]}"; do
            echo "Device detected at $port."

            # Prompt for email and broker password
            email=$(get_input "Enter email address")
            broker_password=$(get_input "Enter broker password")

            # Check if device was unplugged during input
            if [ ! -e "$port" ]; then
                echo "Device unplugged before input completed. Waiting for new device..."
                continue
            fi

            # Create the configuration directory and file
            config_dir="${BASE_CONFIG_DIR}/${email}"
            config_file="${config_dir}/MQTT_CONFIG.py"
            mkdir -p "$config_dir"
            
            # Write configuration to file
            cat <<EOL > "$config_file"
# MQTT Configuration
MQTT_USERNAME = b"$email"
MQTT_PASSWORD = b"$broker_password"
MQTT_SERVER=b"mqtt.super8.dev"
MQTT_CLIENT_ID="$email"
EOL
            echo "Configuration file created at: $config_file"

            # TODO: Use Python library from super8-register here
            # Send a POST request with the email and password (optional)
            url="http://edgelord.hm.unnecessary.llc:8008/register"  # Replace with the actual URL
            response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$url" \
              -H "Content-Type: application/json" \
              -d "{\"username\": \"$email\", \"password\": \"$broker_password\"}")

            if [ "$response" -eq 200 ]; then
                echo "POST request successful."
            else
                echo "POST request failed: HTTP code $response"
            fi

            # Copy files to the device
            copy_files "$port" "$config_dir"

            # Reset device after copying files
            echo "Resetting the device..."
            #rshell -p $port repl "~\x03~"  # Stop running scripts
            #rshell -p $port repl "~\x04~"  # Soft reset

            # Wait for device to be unplugged before continuing
            echo "Please unplug the device to complete the process."
            while [ -e "$port" ]; do
                sleep 1
            done

            echo "Device unplugged. Process complete. Waiting for the next device..."
        done
    fi

    # Update the list of previous ports
    previous_ports=("${current_ports[@]}")
    sleep 1
done
