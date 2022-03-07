# Olhando para todos os dados disponíveis na fonte citada acima, em qual estrutura de banco de dados você orienta guardá-los no nosso Data Lake? SQL ou NoSQL?

Com base na estrutura dos dados atuais, recomendo armazenar em um banco de dados relacional (SQL), uma vez que o esquema de dados para ambos os arquivos está bem definido e possívelmente não passará por mudanças constantes. Apesar de alguns arquivos possuírem um volume de dados considerável, não vejo um aumento neste volume de forma exponencial. Assim, a princípio não vejo escalabilidade como requisito não-funcional para este cenário, o que justificaria a adoção de um banco NoSQL.