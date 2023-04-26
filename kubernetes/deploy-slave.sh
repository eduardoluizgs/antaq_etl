# instala as ferramentas do kubernetes
sudo apt-get install -y kubelet kubeadm

## Adicionando os nós de trabalho ao cluster
sudo kubeadm join 192.168.1.2:6443 --token <token> \
        --discovery-token-ca-cert-hash <sha256:token>
kubectl get nodes
