# -*- mode: ruby -*-
# vi: set ft=ruby ts=2 sw=2 expandtab :

Vagrant.configure(2) do |config|
  # config.vm.box = "ubuntu/trusty64"
  # config.vm.box_check_update = false

  config.vm.synced_folder ".", "/vagrant/orloclient",
     type: "virtualbox", create: "true", owner: "vagrant"

  config.vm.provider "virtualbox" do |vb|
    vb.cpus = "2"
  end

  config.vm.provision "shell", inline: <<-SHELL
    sudo localedef -i en_GB -f UTF-8 en_GB.UTF-8
    sudo locale-gen en_GB.UTF-8
    sudo sed -i 's/us.archive.ubuntu.com/nl.archive.ubuntu.com/g' /etc/apt/sources.list
#     sudo sed -i 's/us.archive.ubuntu.com/repositories.ecg.so/g' /etc/apt/sources.list
#     sudo sed -i 's/httpredir.debian.org/repositories.ecg.so/g' /etc/apt/sources.list

    sudo apt-get -qq update

    # Build/test tools
    apt-get -y install \
      build-essential \
      debhelper \
      dh-systemd \
      git-buildpackage \
      postgresql-client \
      mysql-client \
      python-all-dev \
      python-dev \
      python-pip \
      python-stdeb \
      python-virtualenv \
      python3-all-dev \
      python3-dev \
      python3-pip \
      python3-stdeb \
      python3-virtualenv \
      python3-dev \
      tmux \
      vim \

    # python-ldap dependencies
    apt-get install -y \
      python-dev \
      libldap2-dev \
      libsasl2-dev \
      libssl-dev \

    # Updating build tooling can help
    sudo pip install --upgrade \
      pip \
      setuptools \
      stdeb \
      virtualenv \

    wget -P /tmp/ \
        'http://launchpadlibrarian.net/291737817/dh-virtualenv_1.0-1_all.deb'
    dpkg -i /tmp/dh-virtualenv_1.0-1_all.deb
    apt-get -f install -y


    # Setup virtualenvs; avoids conflicts, particularly with python-six
    virtualenv /home/vagrant/virtualenv/orlo_py27 --python=python2.7
    source /home/vagrant/virtualenv/orlo_py27/bin/activate
    cd /vagrant/orlo
    pip install .[test]
    pip install .[doc]
    python setup.py develop

    virtualenv /home/vagrant/virtualenv/orlo_py34 --python=python3.4
    source /home/vagrant/virtualenv/orlo_py34/bin/activate
    cd /vagrant/orlo
    pip install .[test]
    pip install .[doc]
    python setup.py develop

    echo "source ~/virtualenv/orlo_py34/bin/activate" >> /home/vagrant/.profile

    mkdir -p /etc/orlo /var/log/orlo
    chown -R vagrant:root /etc/orlo /var/log/orlo
    chown -R vagrant:vagrant /home/vagrant/virtualenv
    chown vagrant:root /vagrant

    apt-get -y install postgresql postgresql-server-dev-all
    echo "CREATE USER orlo WITH PASSWORD 'password'; CREATE DATABASE orlo OWNER orlo; " \
        | sudo -u postgres -i psql
  SHELL

  config.vm.define "jessie" do |jessie|
    jessie.vm.box = "bento/debian-8.7"
    jessie.vm.network "forwarded_port", guest: 5000, host: 6134
    jessie.vm.network "private_network", ip: "192.168.57.20"
  end

end
