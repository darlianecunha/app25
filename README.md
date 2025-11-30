# Monitor de editais Alemanha focado em sustentabilidade e mudanças climáticas

Este repositório contém um pequeno robô em Python que monitora notícias de editais, bolsas e oportunidades de pesquisa relacionadas à Alemanha, com foco em sustentabilidade, transição energética e mudanças climáticas.  

O script faz buscas automáticas no Google News em inglês, alemão e português, filtra resultados por termos específicos ligados a agências alemãs (DAAD, DFG, Humboldt, BMBF etc.) e envia um resumo por e mail para o endereço configurado nas variáveis de ambiente.

## Estrutura do projeto

O arquivo `monitor_editais_exterior.py` é o núcleo do monitor e contém toda a lógica de busca, filtragem, formatação dos resultados e envio de e mail.  

O arquivo `run_editais_exterior.py` apenas importa a função principal `main` do monitor e a executa, o que facilita a chamada a partir de workflows e automações.  

O arquivo `requirements.txt` lista as dependências mínimas para rodar o projeto.  

O arquivo `sources_editais_exterior.yaml` guarda links de fontes oficiais da Alemanha que podem ser usados como complemento estático na análise de editais e chamadas.

## Como funciona

O monitor consulta o Google News RSS para uma lista de termos relacionados a Alemanha, sustentabilidade e mudanças climáticas.  

Para cada termo, o script faz buscas em três combinações de idioma e país: inglês com Estados Unidos, alemão com Alemanha e português com Brasil. Os resultados são filtrados por data, deduplicados por link ou título e ordenados dos mais recentes para os mais antigos.  

Ao final, o script monta um e mail em texto simples e HTML com tabelas contendo data, título e link das chamadas encontradas e envia esse relatório para o endereço configurado.

## Configuração

Antes de rodar o projeto é necessário instalar as dependências e definir algumas variáveis de ambiente.  

Instalação das dependências:

```bash
pip install -r requirements.txt
