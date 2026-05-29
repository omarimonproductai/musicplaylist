# incoming/ — zona on deixar les dades de noves llistes

Aquí és on deixes el material perquè es pugi a Cloudinary i es generin els JSON
de les llistes. Una **subcarpeta per llista**, amb el nom curt (slug) que vols
a la URL (ex. `ligabue`, `max_pezzali`).

```
incoming/<slug>/
├── manifest.csv         # ordre + metadades de cada cançó (vegeu sota)
├── 01 - Nom canço.mp4   # àudio (obligatori per cançó)
├── 01 - Nom canço.txt   # lletra simple (opcional)
├── 01 - Nom canço.lrc   # lletra sincronitzada (opcional)
├── 02 - ...
```

Els fitxers es lliguen a cada cançó pel **prefix de número** (`01`, `02`…), que
ha de coincidir amb la columna `num` del manifest.

## manifest.csv

Capçalera obligatòria. Una fila per cançó:

```csv
num,title,artist,youtube
01,I Duri Hanno Due Cuori,Ligabue,https://www.youtube.com/watch?v=brG9lucBdqM
02,Sulla mia strada,Ligabue,
```

- `youtube` és opcional (deixa-ho buit si no n'hi ha).
- `lyrics` i `lrc` no van al manifest: es detecten pels fitxers `.txt` / `.lrc`.

## Què passa després

Amb les credencials de Cloudinary disponibles (`CLOUDINARY_URL`), es genera tot
amb:

```bash
CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@dmtnhepkp \
    python3 tools/build_playlist.py <slug> --title "Títol visible de la llista"
```

Això puja els fitxers a Cloudinary, crea `playlists/<slug>.json` i afegeix el
slug a `playlists/index.json` perquè surti al selector.

## Com fer arribar els fitxers (contenidor remot)

Treballo en un contenidor efímer al núvol, així que els `.mp4`/`.txt`/`.lrc`
m'han d'arribar per algun canal:

- **Via git**: fas commit dels fitxers dins `incoming/<slug>/` a la branca de
  treball i jo els recullo. Senzill, però els `.mp4` són pesats i queden a
  l'historial; un cop pujats a Cloudinary convé eliminar-los del repo.
- **Via URL temporal**: deixes els fitxers en un enllaç descarregable (Drive,
  WeTransfer, etc.) i jo els baixo al contenidor abans de pujar-los.

Les **credencials** (`CLOUDINARY_URL` amb api_key:api_secret) no van mai al repo:
es passen com a variable d'entorn de l'entorn o me les dius al xat per a un ús
puntual de la sessió.
