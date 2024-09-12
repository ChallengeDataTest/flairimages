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

## directories

- `data/` : les données Flair#1
- `src/` : le code de travail
- `.devcontainer/` : configuration pour le développement dans un conteneur Docker (VSCode)
- `.github/` : configuration pour les actions GitHub
- `outputs/` : les résultats de l'inférence

## working in containers

- vscode :
  - `code .` dans le répertoire racine
  - `F1` puis `Remote-Containers: Reopen in Container`
  - retour en local (utile pour Git): `F1` puis `devcontainer: Reopen folder locally`

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
### masques

| ID  | Description              | Color   |
|-----|--------------------------|---------|
| 1   | bâtiment                 | `#db0e9a` ![#db0e9a](data:image/gif;base64,0lGODlhAQABAPAAAMsOmgAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 2   | surface perméable        | `#938e7b` ![#938e7b](data:image/gif;base64,R0lGODlhAQABAPAAAJOOewAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 3   | surface imperméable      | `#f80c00` ![#f80c00](data:image/gif;base64,R0lGODlhAQABAPAAAPgMAAAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 4   | sol nu                   | `#a97101` ![#a97101](data:image/gif;base64,R0lGODlhAQABAPAAAKlxAQAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 5   | eau                      | `#1553ae` ![#1553ae](data:image/gif;base64,R0lGODlhAQABAPAAAGVOqQAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 6   | conifère                 | `#194a26` ![#194a26](data:image/gif;base64,R0lGODlhAQABAPAAAGUqJAAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 7   | décidu                   | `#46e483` ![#46e483](data:image/gif;base64,R0lGODlhAQABAPAAAG5+gwAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 8   | buisson                  | `#f3a60d` ![#f3a60d](data:image/gif;base64,R0lGODlhAQABAPAAAPOaDQAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 9   | vignoble                 | `#660082` ![#660082](data:image/gif;base64,R0lGODlhAQABAPAAAJgAigAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 10  | végétation herbacée      | `#55ff00` ![#55ff00](data:image/gif;base64,R0lGODlhAQABAPAAAP8A/wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 11  | terre agricole           | `#fff30d` ![#fff30d](data:image/gif;base64,R0lGODlhAQABAPAAAP8A/wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 12  | terre labourée           | `#e4df7c` ![#e4df7c](data:image/gif;base64,R0lGODlhAQABAPAAAP8A/wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 13  | piscine                  | `#3de6eb` ![#3de6eb](data:image/gif;base64,R0lGODlhAQABAPAAAP8A/wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 14  | neige                    | `#ffffff` ![#ffffff](data:image/gif;base64,R0lGODlhAQABAPAAAP8A/wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 15  | coupe à blanc            | `#8ab3a0` ![#8ab3a0](data:image/gif;base64,R0lGODlhAQABAPAAAP8A/wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |
| 16  | mixte                    | `#6b714f` ![#6b714f](data:image/gif;base64,R0lGODlhAQABAPAAAP8A/wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==) |