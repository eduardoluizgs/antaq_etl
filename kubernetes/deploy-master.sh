# instala o pacote de transporte https e o curl
sudo apt install apt-transport-https curl

# adiciona a chave de assinatura do Kubernetes
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add

# adiciona o repositório Kubernetes como uma fonte de pacote
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" >> ~/kubernetes.list
sudo mv ~/kubernetes.list /etc/apt/sources.list.d

# atualiza a lista de pacotes
sudo apt update

# desabilita a swap memory durante a sessão atual
sudo swapoff -a

# desabilita a swap memory na reinicialização
# comentar a linha da swap dentro do arquivo fstab
sudo nano /etc/fstab

# ajusta nome do host
sudo hostnamectl set-hostname kubernetes-master

# verifica se o módulo br_netfilter está carregado
lsmod | grep br_netfilter

# caso não esteja, vamos carregá-lo
sudo modprobe br_netfilter

# configura o iptables para permitir o tráfego em bridge
sudo sysctl net.bridge.bridge-nf-call-iptables=1

sudo apt install docker.io -y

sudo mkdir /etc/docker
cat <<EOF | sudo tee /etc/docker/daemon.json
{ "exec-opts": ["native.cgroupdriver=systemd"],
"log-driver": "json-file",
"log-opts":
{ "max-size": "100m" },
"storage-driver": "overlay2"
}
EOF

# habilita o serviço docker na inicialização do sistema
sudo systemctl enable docker

# recarrega o daemon
sudo systemctl daemon-reload

# restart o serviço do docker
sudo systemctl restart docker

sudo ufw allow 6443
sudo ufw allow 6443/tcp

sudo nano /etc/netplan/01-netcfg.yaml

# conteudo do arquivo
# network:
#   ethernets:
#     ens33:
#       addresses: [192.168.1.100/24]
#       gateway4: 192.168.1.1
#       nameservers:
#         addresses: [192.168.1.1, 8.8.8.8]
#  version: 2

# verificar se a configuração está correta
sudo netplan try

# instala as ferramentas do kubernetes
sudo apt-get install -y kubelet kubeadm kubectl kubernetes-cni

sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# cria a pasta home do kubernets para o usuário atual
mkdir -p $HOME/.kube

#  copioa o arquivo de configuração para a pasta do usuário atual
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config

# seta permissões para o arquivo de conmfiguração do usuário atual
sudo chown $(id -u):$(id -g) $HOME/.kube/config

kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/k8s-manifests/kube-flannel-rbac.yml

# mostra o status dos serviços do kubernets
kubectl get pods --all-namespaces

# verifica integridade dos componentes
kubectl get componentstatus

# ou
kubectl get cs

# edita a linha spec->containers->command contendo a linha - --port=0
sudo nano /etc/kubernetes/manifests/kube-scheduler.yaml
sudo nano /etc/kubernetes/manifests/kube-controller-manager.yaml

# reinicia o serviço do kubernets
sudo systemctl restart kubelet.service
