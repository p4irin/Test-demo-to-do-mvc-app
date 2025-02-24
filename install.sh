#!/usr/bin/bash

# 1. Install Playwright Pytest plugin including Playwright and Pytest
#    in a Python virtual environment
# 2. Install default browsers and their system dependencies

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_PYTHON_VERSION="3.8"
if [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_PYTHON_VERSION" | sort -V | head -n1) != "$REQUIRED_PYTHON_VERSION" ]]; then
  echo "Python 3.8 or higher is required. You have Python $PYTHON_VERSION."
  exit 1
fi

# Check OS version
OS_NAME=$(lsb_release -is)
OS_VERSION=$(lsb_release -rs)
if [[ "$OS_NAME" != "Debian" && "$OS_NAME" != "Ubuntu" ]]; then
  echo "This script supports only Debian and Ubuntu."
  exit 1
fi

if [[ "$OS_NAME" == "Debian" && "$OS_VERSION" != "12" ]]; then
  echo "Debian 12 is required. You have Debian $OS_VERSION."
  exit 1
fi

if [[ "$OS_NAME" == "Ubuntu" && "$OS_VERSION" != "22.04" && "$OS_VERSION" != "24.04" ]]; then
  echo "Ubuntu 22.04 or 24.04 is required. You have Ubuntu $OS_VERSION."
  exit 1
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
# Install Playwright Pytest plugin
# This will also install Playwright and Pytest
pip install pytest-playwright pytest-html

# Install default browsers and their system dependencies
playwright install --with-deps

echo ""
echo "Default browsers are installed in ~/.cache/ms-playwright"
echo "Make sure you activate the virtual environment"
echo "Put your tests in the 'tests' directory"
echo "Configure pytest options in pytest.ini"
echo "Run tests with 'pytest' command"
