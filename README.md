# TCC-NFS-GLUSTER-CEPH

## Resumo

Este repositório contém todo o material do Trabalho de Conclusão de Curso (TCC) que compara soluções de armazenamento distribuído: NFS, GlusterFS e Ceph. O objetivo é avaliar o desempenho, facilidade de configuração e uso dessas tecnologias em ambientes Linux, especialmente para persistência de dados em sistemas distribuídos.

### Estrutura do Repositório

- **materiais/**: Contém os arquivos de configuração e scripts para testes de benchmark.
	- **nfs/**: YAMLs para provisionamento e teste de volumes NFS.
	- **gluster/**: YAMLs para provisionamento e teste de volumes GlusterFS.
	- **ceph/**: YAMLs para provisionamento e teste de volumes Ceph.
	- **preparaAmbiente/**: Scripts de preparação e benchmark, como o `script-benchmark.sh`.
- **resultados/**: Diretórios para armazenar os resultados dos testes de cada solução.
- **README.md**: Este arquivo, com instruções e resumo do projeto.
- **LICENSE**: Licença do projeto.

### Como utilizar

1. Configure o ambiente conforme os arquivos em `materiais/` para cada solução de armazenamento.
2. Utilize o script de benchmark para executar os testes de desempenho.
3. Os resultados serão salvos na pasta `resultados/`.

### Objetivo

O projeto visa fornecer uma análise comparativa entre NFS, GlusterFS e Ceph, auxiliando na escolha da melhor solução de armazenamento distribuído para diferentes cenários.