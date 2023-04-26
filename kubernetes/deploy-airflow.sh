# Adiciona repositório do helm
helm repo add apache-airflow https://airflow.apache.org/

# realiza implantação do serviço do airflow
helm install airflow apache-airflow/airflow --version 1.9.0

# realiza remoção do serviço
# helm uninstall airflow
