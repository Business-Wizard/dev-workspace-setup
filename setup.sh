sudo apt-get update && \

sudo apt install curl && \
sudo apt-get install git && \
curl https://pyenv.run | bash && \
echo "export PYENV_ROOT=\"\$HOME/.pyenv\"" >> ~/.bashrc && \
echo "command -v pyenv >/dev/null || export PATH=\"\$PYENV_ROOT/bin:\$PATH\"" >> ~/.bashrc && \
echo "eval \"\$(pyenv init -)\"" >> ~/.bashrc && \

sudo snap install code-insiders && \
echo "alias code=\"code-insiders\"" >> ~/.bashrc && \

sudo apt install wireguard && \
wget -O torguard_install.deb \
https://torguard.net/downloads/new/torguard-latest-amd64.deb && \
sudo apt install ./torguard_install.deb || \
rm -f torgaurd_install.deb || \

sudo add-apt-repository ppa:graphics-drivers/ppa && \
sudo ubuntu-drivers autoinstall && \

sudo apt-get install dkms librm-dev
