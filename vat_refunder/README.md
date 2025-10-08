sudo dnf install docker docker-compose-plugin python3 python3-mysql-connector
sudo systemctl enable --now docker

# start database
docker compose up -d

mkdir -p ~/Desktop/exports
cp /home/$USER/vat_refunder/vat_refunder.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
chmod +x ~/.local/share/applications/vat_refunder.desktop
