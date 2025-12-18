#!/bin/bash

LOOPS=50
SOURCE_DIR="/tmp"
DEST_DIR="/mnt"

FILES=("arquivo_1GB.img" "arquivo_3GB.img" "arquivo_5GB.img" "arquivo_7GB.img")

echo "--- Iniciando Bateria de Testes de Persistencia ---"
echo "Destino NFS: $DEST_DIR | Repetições: $LOOPS"

if [ ! -d "$DEST_DIR" ]; then
    echo "ERRO CRITICO: Diretorio $DEST_DIR nao encontrado! Verifique a montagem."
    exit 1
fi

for FILE in "${FILES[@]}"; do
    SOURCE_PATH="$SOURCE_DIR/$FILE"
    OUTPUT_CSV="resultado_nfs_${FILE}.csv"
    
    echo "=================================================="
    echo "Iniciando bateria para: $FILE"
    
    if [ ! -f "$SOURCE_PATH" ]; then
        echo "AVISO: Arquivo fonte $SOURCE_PATH inexistente. Pulando..."
        continue
    fi

    echo "Real(s);User(s);Sys(s);CPU_Usage" > $OUTPUT_CSV

    for i in $(seq 1 $LOOPS); do
        echo "  -> [ $FILE ] Execucao $i de $LOOPS..."
        
        rm -f "$DEST_DIR/$FILE"
        
        /usr/bin/time -f "%e;%U;%S;%P" sh -c "cp $SOURCE_PATH $DEST_DIR/ && sync" 2>> $OUTPUT_CSV
    done

    echo "Finalizado para $FILE. Dados salvos em: $OUTPUT_CSV"
done

echo "=================================================="
echo "Experimento concluido com sucesso."