# 🌾 FarmTech Solutions — Agrotech
### Sistema de Gestão de Perdas na Colheita de Cana-de-Açúcar

---

Oi! Vou te contar sobre o projeto que desenvolvi aqui na faculdade. Pode parecer um nome difícil, mas prometo que a ideia por trás disso é bem simples — e bem legal.

---

## O que eu fiz e por quê

Sabe que o Brasil é o maior produtor de cana-de-açúcar do mundo, né? Pois é. A gente colhe mais de **620 milhões de toneladas por safra**. Um número absurdo. Mas tem um problemão que pouca gente fala: **uma parte enorme dessa cana vai embora durante a colheita e ninguém nem percebe.**

Quando a colheita é feita por máquinas (que é o caso da maioria das grandes fazendas hoje), a perda chega a **15% da produção**. Quando é feita à mão, essa perda cai para menos de 5%. Parece pouco? Só no estado de São Paulo, que tem cerca de 3 milhões de hectares plantados, isso representa uma perda estimada de **R$ 20 milhões por ano**. Impressionante, né?

Aí veio a ideia: **e se eu fizesse um sistema que ajudasse o produtor a enxergar esse prejuízo de forma clara?** Que mostrasse, em reais, quanto cada fazenda está perdendo e se ela está bem ou mal comparada com as referências do setor?

Foi isso que eu construí.

---

## Sobre o projeto em si

Esse projeto é a continuação de dois trabalhos anteriores que já tinha feito aqui na faculdade. No primeiro, criei um sistema simples de controle agrícola para Shitake e Horticultura. No segundo, montei um sistema de irrigação inteligente com ESP32. Agora, na Fase 3, o desafio era evoluir tudo isso usando Python de verdade — com banco de dados Oracle, arquivos JSON, estruturas de dados e muito mais.

**Disciplina:** Computational Thinking with Python  
**Tutor(a):** Sabrina Otoni  
**Coordenador(a):** André Godoi  
**Desenvolvido por:** Fred Eric Nascimento Santos

---

## Como o sistema funciona

A ideia principal é simples: o produtor entra com os dados da colheita (fazenda, área, quanto produziu, quanto perdeu) e o sistema faz todo o resto.

Ele calcula a perda em toneladas, converte isso em reais usando o preço de referência da UNICA (R$ 120,00/t), e ainda diz se aquela fazenda está indo bem ou mal baseado nas referências técnicas da SOCICANA:

- 🟢 **EXCELENTE** — perda bem abaixo do esperado pro tipo de colheita
- 🔵 **BOM** — dentro de um patamar aceitável
- 🟡 **ATENÇÃO** — já na faixa de risco
- 🔴 **CRÍTICO** — acima do limite, precisa agir rápido

E no final, o sistema gera um relatório mostrando qual fazenda foi melhor, qual foi pior, quanto foi perdido no total e quanto poderia ser economizado se todas atingissem a meta de 5%.

---

## O que aprendi e coloquei em prática

Aqui vai a parte mais técnica, mas vou tentar explicar de um jeito fácil:

**Funções e Procedimentos (Capítulo 3)**
Aprendi que em Python dá pra criar "blocos" de código que fazem uma coisa específica e podem receber valores para trabalhar. Por exemplo, criei uma função chamada `calcular_perda_estimada()` que recebe a produção, o tipo de colheita e o percentual de perda, e devolve quanto foi perdido em toneladas, em reais e qual o status. É tipo uma calculadora especializada.

**Estruturas de Dados (Capítulo 4)**
Aqui aprendi sobre três tipos de "caixas" para guardar informações:
- **Tupla** — uso pra coisas que não mudam, como os tipos de colheita possíveis (`"Manual"` e `"Mecanizada"`) e as faixas de perda do setor. É como um valor fixo mesmo.
- **Dicionário** — minha estrutura principal. Cada lote de colheita é um dicionário com todas as informações daquele registro. E todos os lotes ficam num dicionário maior, que funciona como uma mini-tabela na memória.
- **Lista** — uso pra ordenar, filtrar e gerar os relatórios.

**Arquivos (Capítulo 5)**
O sistema salva tudo em dois formatos:
- **JSON** — um arquivo organizado que o sistema lê toda vez que é aberto, pra não perder os dados ao fechar.
- **TXT** — um relatório bonitinho pra imprimir ou compartilhar com o produtor.

**Banco de Dados Oracle (Capítulo 6)**
Aqui foi o mais desafiador. Aprendi a conectar o Python com o Oracle Database, criar a tabela direto pelo código, inserir registros e fazer consultas. O legal é que o sistema funciona normalmente mesmo sem o Oracle configurado — os dados ficam salvos em JSON. Mas quando o banco está disponível, tudo é guardado lá também, de forma mais segura e profissional.

---

## Estrutura dos arquivos

```
farmtech-fase3/
│
├── python/
│   ├── app.py                        → o coração do projeto, todo o sistema está aqui
│   └── oracle_config.template.json  → modelo de configuração pro banco Oracle
│
├── r/
│   └── analise_cana.R               → análise estatística dos dados + previsão do tempo
│
├── sql/
│   └── farmtech_oracle.sql          → scripts pra criar e consultar o banco Oracle
│
├── data/
│   ├── lotes_cana.json              → onde os dados ficam salvos entre uma sessão e outra
│   └── relatorio_perdas.txt         → relatório gerado pelo sistema
│
└── README.md                        → esse arquivo aqui :)
```

---

## Como rodar

Se você quiser testar, é bem simples:

**Para rodar o sistema principal:**
```bash
cd python
python app.py
```

O menu vai aparecer assim:
```
1 - Registrar novo lote de colheita
2 - Listar todos os lotes
3 - Atualizar lote
4 - Excluir lote
5 - Relatório analítico de perdas
6 - Gestão de arquivos (JSON / TXT)
7 - Operações Oracle
0 - Sair
```

**Para rodar a análise em R:**
```r
source("r/analise_cana.R", encoding = "UTF-8")
```

Esse script lê o JSON que o sistema Python gerou, calcula médias, ranking de fazendas e ainda puxa a previsão do tempo pra região de Ribeirão Preto — que é o principal polo de cana do Brasil.

**Para usar com Oracle:**
1. Copie o arquivo `oracle_config.template.json` e renomeie pra `oracle_config.json`
2. Coloque suas credenciais reais lá dentro
3. No menu do sistema, vá em opção **7 → 1** pra criar a tabela
4. A partir daí, todo lote inserido vai pro banco automaticamente

> ⚠️ Importante: o `oracle_config.json` com suas senhas nunca vai pro GitHub — já coloquei ele no `.gitignore` justamente pra isso.

---

## A parte do R

Além do Python, o projeto tem uma análise em R que eu achei muito interessante de fazer. Ela:

- Calcula a média, mediana e desvio padrão das perdas
- Separa os números por tipo de colheita (manual vs. mecanizada)
- Mostra um ranking das fazendas da melhor pra pior
- Estima quanto o setor economizaria se todas atingissem a meta de 5%
- Traz a previsão do tempo de Ribeirão Preto/SP direto da API Open-Meteo (gratuita e sem precisar de cadastro)

---

## Por que esse tema?

Quando li sobre o agronegócio pra esse projeto, fiquei impressionado com os números. O Brasil alimenta boa parte do mundo, e a cana-de-açúcar é uma das culturas mais importantes que temos. Saber que existe um desperdício enorme e que tecnologia pode ajudar a reduzir isso me motivou bastante.

Não precisei inventar um problema — ele já existe, está documentado e tem impacto real. O sistema que criei é simples, mas a ideia dele é exatamente essa: dar ao produtor uma ferramenta clara pra enxergar o que está acontecendo no campo e tomar decisões melhores.

---

## Onde encontrar mais informação

Esses foram os materiais que usei como base:

- SOCICANA — referência sobre perdas na colheita mecanizada
- EMBRAPA — agricultura digital e inovação no campo
- TOTVS Blog — o que é agronegócio
- UNICA — dados de produção de cana no Brasil
- Open-Meteo — API de clima gratuita

---

Obrigado por chegar até aqui! Se tiver dúvida sobre qualquer parte do código ou quiser entender melhor alguma lógica, é só perguntar. 🤝
