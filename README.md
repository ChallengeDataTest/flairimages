# flairimages

challenge basé sur la dataset Flair#1 (IGNF)

## Origine des données

voir [Flair#1](https://ignf.github.io/FLAIR/index.html) et/ou l'article: [FLAIR: French Land cover from Aerospace Imagery](https://arxiv.org/pdf/2211.12979.pdf)

Crédits à rappeler pour tout usage des données Flair#1:

```text
Anatol Garioud, Stéphane Peillet, Eva Bookjans, Sébastien Giordano, and Boris Wattrelos. 2022. 
FLAIR #1: semantic segmentation and domain adaptation dataset. (2022). 
DOI:https://doi.org/10.13140/RG.2.2.30183.73128/1
```

## Objectif

  proposer une tâche d'inférence simplifiée sur les données Flair#1.  
  Par exemple distinguer les sols artificialisés des sols naturels.

## This project

### Configuration
- Toutes les metadonnées doivent autant que possible être stockées dans le fichier `[racine du projet]/config/config.yaml`.

### Working in containers

- vscode :
  - `code .` dans le répertoire racine sur la machine hôte
  - `F1` puis `Dev Containers: Reopen in Container`
  - retour en local (utile pour Git): `F1` puis `Dev Containers: Reopen folder locally`

- Docker + Jupyter lab (superficiellemnt testé):
  - dans le répertoire racine, sous bash:

  ```bash
  docker build -t flairimages ./Docker
  
  docker run -i -t --rm \  
    -p 8888:8888 \  
    -v $(pwd):/workspaces/flairimages \ 
    flairimages
  ```
  
  - relever l'ip avec tocken d'accès dans la sortie texte du container, ctrl+Click sur le lien pour ouvrir Jupyter lab dans le navigateur. E.g.:

  ```text
  [C 2024-09-12 18:32:40.454 ServerApp]  
  
    To access the server, open this file in a browser:  
        file:///root/.local/share/jupyter/runtime/jpserver-1-open.html
    Or copy and paste one of these URLs:  
        http://localhost:8888/lab?token=dfba5c534dc12f4f0440a3afd221b908fb52025d87a96b99  
        http://127.0.0.1:8888/lab?token=dfba5c534dc12f4f0440a3afd221b908fb52025d87a96b99  
  [...]
  ```

## Description des données
- images: fichiers IMG_[id].tif à 5 canaux (RGB + infrarouge + élévation)
- masques: fichiers MSK_[id].tif à 1 canal (label)
- les classes  sont décrites avec leurs regroupements dans le fichier `./config/config.yaml`

### Classes
(voir [ce notebook](./src/divers_utils.ipynb) pour générer ce tableau)

| Id | Label | Color | Artificiel |  
|---|-------|-------|---|  
| 1  | bâtiment | <span style="color:#db0e9a; font-size: 20px;">■</span> `#db0e9a` | X |  
| 2  | surface perméable | <span style="color:#938e7b; font-size: 20px;">■</span> `#938e7b` | X |  
| 3  | surface imperméable | <span style="color:#f80c00; font-size: 20px;">■</span> `#f80c00` | X |  
| 4  | sol nu | <span style="color:#a97101; font-size: 20px;">■</span> `#a97101` |  |  
| 5  | eau | <span style="color:#1553ae; font-size: 20px;">■</span> `#1553ae` |  |  
| 6  | conifère | <span style="color:#194a26; font-size: 20px;">■</span> `#194a26` |  |  
| 7  | feuillu | <span style="color:#46e483; font-size: 20px;">■</span> `#46e483` |  |  
| 8  | buisson | <span style="color:#f3a60d; font-size: 20px;">■</span> `#f3a60d` |  |  
| 9  | vignoble | <span style="color:#660082; font-size: 20px;">■</span> `#660082` |  |  
| 10  | végétation herbacée | <span style="color:#55ff00; font-size: 20px;">■</span> `#55ff00` |  |  
| 11  | terre agricole | <span style="color:#fff30d; font-size: 20px;">■</span> `#fff30d` |  |  
| 12  | terre labourée | <span style="color:#e4df7c; font-size: 20px;">■</span> `#e4df7c` |  |  
| 13  | piscine | <span style="color:#3de6eb; font-size: 20px;">■</span> `#3de6eb` | X |  
| 14  | neige | <span style="color:#ffffff; font-size: 20px;">■</span> `#ffffff` |  |  
| 15  | coupe claire | <span style="color:#8ab3a0; font-size: 20px;">■</span> `#8ab3a0` |  |  
| 16  | mixte | <span style="color:#6b714f; font-size: 20px;">■</span> `#6b714f` |  |  
| 17  | ligneux | <span style="color:#c5dc42; font-size: 20px;">■</span> `#c5dc42` |  |  
| 18  | serre | <span style="color:#9999ff; font-size: 20px;">■</span> `#9999ff` | X |  
| 19  | autre | <span style="color:#000000; font-size: 20px;">■</span> `#000000` |  |  



