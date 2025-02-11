# Sistemas Distribuídos

Este projeto implementa um sistema de compartilhamento de arquivos distribuído utilizando sockets e uma interface gráfica com Tkinter. O sistema é composto por um servidor que gerencia os arquivos e múltiplos clientes que podem se conectar ao servidor para compartilhar e sincronizar arquivos.

## Funcionalidades

- **Servidor:**
  - Aceita conexões de múltiplos clientes.
  - Gerencia a lista de arquivos compartilhados.
  - Permite que os clientes criem, deletem e busquem arquivos.
  - Sincroniza a lista de arquivos entre os clientes conectados.

- **Cliente:**
  - Interface gráfica moderna utilizando Tkinter e ttk.
  - Conecta-se ao servidor para compartilhar e sincronizar arquivos.
  - Permite buscar arquivos no servidor.
  - Permite baixar arquivos de outros clientes conectados.
  - Sincroniza a lista de arquivos locais com o servidor.

## Requisitos

- Python 3.6 ou superior
- Tkinter (para a interface gráfica)
- Bibliotecas padrão do Python (socket, threading, json, os)

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/sistemas-distribuidos.git
   cd sistemas-distribuidos
2. Instale as dependências do Tkinter (se necessário):
    ```bash
   sudo apt install python3-tk

## Uso

### Iniciar o Servidor

1. Navegue até o diretório do projeto.
2. Execute o servidor:
    ```bash
    python3 servidor.py

### Iniciar o Cliente

1. Navegue até o diretório do projeto.
2. Execute o cliente:
    ```bash
    python3 clienteGUI.py

## Funcionalidades do Cliente

* Join Server: Conecta o cliente ao servidor especificado.
* Sync Files: Sincroniza a lista de arquivos locais com o servidor.
* Refresh List: Atualiza a lista de arquivos disponíveis no servidor.
* Search File: Busca um arquivo específico no servidor.
* Get File: Baixa um arquivo de outro cliente conectado.
* Leave Server: Desconecta o cliente do servidor.

## Estrutura do Projeto

```bash
.
├── clienteGUI.py       # Código do cliente com interface gráfica
├── servidor.py         # Código do servidor
├── README.md           # Documentação do projeto
└── lista_arquivos.json # Arquivo JSON para armazenar a lista de arquivos (gerado pelo servidor)
```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests para melhorar o projeto.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Contato

Nome: Antonio Marcos | Flávio Henrique  
Email: ambrcz@hotmail.com | flaviohenriquefc@gmail.com   
GitHub: AntonioMarcosDev | ndbzika  

Obrigado por usar o sistema de compartilhamento de arquivos distribuído! Se você tiver alguma dúvida ou sugestão, não hesite em entrar em contato.

