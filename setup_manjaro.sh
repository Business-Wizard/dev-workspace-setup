sudo pacman -Syu && \
sudo pamac checkupdates -a && \
sudo pamac upgrade -a && \
sudo sed -Ei '/EnableAUR/s/^#//' /etc/pamac.conf && \


mkdir install_dir && \
cd install_dir && \


sudo wget https://raw.githubusercontent.com/archlinux/svntogit-packages/packages/base-devel/trunk/PKGBUILD && \
echo "Y" | makepkg -si && \
sudo rm -rf ./* && \


git clone https://aur.archlinux.org/visual-studio-code-insiders-bin.git && \
cd visual-studio-code-insiders-bin && \
echo "Y" | makepkg -si && sudo pacman -U && \
cd .. && \
sudo rm -rf ./* && \
echo "alias code=\"code-insiders\"" >> ~/.bashrc && \
echo "alias code=\"code-insiders\"" >> ~/.zshrc && \


curl https://pyenv.run | bash && \
echo "export PYENV_ROOT=\"\$HOME/.pyenv\"" >> ~/.bashrc && \
echo "command -v pyenv >/dev/null || export PATH=\"\$PYENV_ROOT/bin:\$PATH\"" >> ~/.bashrc && \
echo "eval \"\$(pyenv init -)\"" >> ~/.bashrc && \
echo "export PYENV_ROOT=\"\$HOME/.pyenv\"" >> ~/.zshrc && \
echo "command -v pyenv >/dev/null || export PATH=\"\$PYENV_ROOT/bin:\$PATH\"" >> ~/.zshrc && \
echo "eval \"\$(pyenv init -)\"" >> ~/.zshrc && \
exec $SHELL && \


python -m ensurepip --upgrade && \
echo "alias pip=\"pip3\"" >> ~/.bashhrc && \
echo "alias pip=\"pip3\"" >> ~/.zshrc && \
exec $SHELL && \


pip install pipx && pipx install poetry && \
pipx install black && pipx install ruff && pipx install poetry && \
poetry config virtualenvs.create true && \
poetry config virtualenvs.in-project true && \

pyenv install 3.11 || pyenv install 3.10 || \


curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y


echo "Y" | sudo pacman -S wireguard-tools && \
wget -O torguard_install.tar.gz \
https://torguard.net/downloads/new/torguard-latest-amd64-arch.tar.gz && \
find ./ -iname "tor*.tar.gz" | xargs tar xf && \
cd $(find ./ -name "torguard*arch")  && \
echo "Y" | makepkg -si && \
cd .. && \
sudo rm -rf ./*
