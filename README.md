# Chronos
A ideia é pegar os dados do controle de ponto feito pelo Notion e, através de um script, gerar um PDF com os devidos registros.

# Link para o template do Notion
https://spiny-show-231.notion.site/Controle-de-Ponto-Template-32e324789a528073a35debd80ad99f76

# Como configurar a API do Notion
1. Duplique a página de template do link disponibilizado acima em seu espaço pessoal.
2. Acesse o notion.so/my-integrations.
3. Crie uma nova integração (uma sugestão de nome é "Exportador de Ponto") no espaço correto.
4. Sugiro que reduza as capabilities para apenas leitura. Mantenha o "Internal integration secret" a disposição.
5. Vá na sua página Controle de Ponto, clique nos três pontos (...) no canto superior direito, desça até "Conexões" e adicione a integração criada.
6. Copie o ID do banco de dados dos pontos. Isso pode ser feito abrindo a DB pelo Notion, clicando nos três pontos (...) no canto superior direito, clicando em "copiar link" e copiando os 32 caracteres antes da interrogação. Exemplo: https://www.notion.so/abcdefghijklmnopqrstuvwxyz123456?v=311324789a52807f87dc000cec08b63f&source=copy_link (Nesse caso, o ID da DB é "abcdefghijklmnopqrstuvwxyz123456").
7. Crie um arquivo .env no root do projeto definindo NOTION_TOKEN e DATABASE_ID com os valores obtidos.
8. Nesse mesmo .env criado, defina também NAME e TITLE: NAME é o seu nome e TITLE é o título do XLSL gerado.
    Exemplo:
    NAME = "Matheus"
    TITLE = "Lançamento Horas"

    Ao executar python .\generateShiftXlsl.py 02-2026, o arquivo gerado será o "Matheus - Lançamento Horas - 02-2026"

# Executando o script

