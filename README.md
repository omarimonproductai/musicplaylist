# Music Playlist

Web estàtic (només HTML + JSON, sense servidor propi) per escoltar llistes de
cançons amb àudio i lletres (simples o sincronitzades tipus karaoke). L'àudio i
les lletres es guarden a [Cloudinary](https://cloudinary.com); al repositori
només hi ha les pàgines i un JSON per llista.

---

## 1. Com funciona (visió general)

| Fitxer / carpeta | Què és |
|---|---|
| `playlist_selector.html` | **Pàgina d'entrada.** Llista totes les playlists. |
| `playlist.html` | Cançons d'una playlist concreta. |
| `player.html` | Reproductor: àudio + lletra (mode simple o karaoke `.lrc`) + botó de vídeo de YouTube. |
| `playlists/index.json` | Índex: llista de *slugs* que surten al selector. |
| `playlists/<slug>.json` | Dades d'una playlist (títol + cançons amb les seves URLs). |
| `incoming/<slug>/` | Zona de treball on deixes els fitxers d'una llista nova abans de generar-la. |
| `tools/build_playlist.py` | Script que puja els mèdia a Cloudinary i genera `playlists/<slug>.json`. |
| `.github/workflows/build-playlist.yml` | El mateix procés, però executat a GitHub Actions. |

Dos noms importants per cada llista:

- **Títol**: el text visible (ex. `Lax'n'Busto - Cap Roig 06/08/2026`). Pot tenir
  espais, accents, barres… és lliure.
- **Slug**: nom curt per a la carpeta i la URL (ex. `laxnbusto_cap_roig`). Sense
  espais, accents ni símbols; només lletres, números i guions baixos.

---

## 2. Veure el web localment

Les pàgines carreguen les dades amb `fetch()`, i els navegadors **bloquegen
`fetch()` quan obres un fitxer amb doble clic** (`file://`). Per això cal servir
la carpeta amb un petit servidor HTTP local (això és el "port de localhost").

Des de l'arrel del projecte, tria **una** opció:

```bash
python3 -m http.server 8000      # Python
# o
npx serve -l 8000                # Node
# o
php -S localhost:8000            # PHP
```

Després obre al navegador:

```
http://localhost:8000/playlist_selector.html
```

> L'àudio i les lletres viuen a Cloudinary (URLs externes), així que per
> **reproduir** cançons cal connexió a internet. El servidor local només serveix
> els HTML i els JSON.

---

## 3. Crear una playlist nova (guia pas a pas)

### Pas 1 — Tria el slug

Un nom curt sense espais ni accents. Exemples: `ligabue`, `laxnbusto_cap_roig`.

### Pas 2 — Prepara la carpeta `incoming/<slug>/`

Crea la carpeta i posa-hi els fitxers de cada cançó. **Cada cançó es lliga als
seus fitxers pel prefix numèric** (`01`, `02`, …), que ha de coincidir amb la
columna `num` del manifest:

```
incoming/<slug>/
├── manifest.csv           # ordre + metadades (obligatori)
├── 01 - Nom cançó.m4a     # àudio  (obligatori per cançó; també val .mp4)
├── 01 - Nom cançó.txt     # lletra simple        (opcional)
├── 01 - Nom cançó.lrc     # lletra sincronitzada (opcional, mode karaoke)
├── 02 - ...
```

Regles del lligam de fitxers:

- **Àudio** (`.m4a` o `.mp4`): obligatori. Sense àudio, la cançó apareix però no
  es pot reproduir.
- **`.txt`**: lletra simple (text pla). Opcional.
- **`.lrc`**: lletra amb marques de temps → activa el mode karaoke. Opcional.
- Els `.txt` i `.lrc` **no** es posen al manifest: es detecten sols pel número.
- N'hi ha prou que el nom **comenci** amb el número (`01 - qualsevol cosa.m4a`);
  la resta del nom és lliure.

### Pas 3 — Escriu el `manifest.csv`

Capçalera obligatòria, una fila per cançó:

```csv
num,title,artist,youtube
01,La meva terra es el mar,Lax'n'Busto,
02,Trepitja fort,Lax'n'Busto,https://www.youtube.com/watch?v=XXXXXXXXXXX
```

- `num`: el número que coincideix amb el prefix dels fitxers (`01`, `02`…).
- `title`: títol visible de la cançó.
- `artist`: intèrpret.
- `youtube`: enllaç del vídeo (opcional; deixa'l buit si no n'hi ha).
- Fitxer en **UTF-8**. No cal cometes si el text no conté comes.

### Pas 4 — Genera la llista

Cal el compte de Cloudinary. Hi ha **dues maneres** (fan exactament el mateix:
pugen els mèdia a Cloudinary, creen `playlists/<slug>.json` i afegeixen el slug a
`playlists/index.json`).

#### Opció A — GitHub Actions (recomanada)

Les credencials no surten mai de GitHub.

1. **Requisit únic**: al repo, *Settings → Secrets and variables → Actions*, han
   d'existir els secrets `CLOUDINARY_API_KEY` i `CLOUDINARY_API_SECRET`.
   (El *cloud name* està fixat dins del workflow.)
2. Fes **commit i push** de la carpeta `incoming/<slug>/` (manifest + mèdia) a
   una branca.
3. Ves a *Actions → "Build playlist" → Run workflow* i omple:
   - **Use workflow from**: la branca on has pujat els fitxers.
   - **slug**: el teu slug (ex. `laxnbusto_cap_roig`).
   - **title**: el títol visible (ex. `Lax'n'Busto - Cap Roig 06/08/2026`).
   - **front**: marca-ho si vols que la llista surti a dalt de tot del selector.
4. El workflow fa commit de `playlists/<slug>.json` i `index.json` a la mateixa
   branca. Fes `git pull` i ja està.

> Pots pujar els mèdia des de la web de GitHub: entra a la carpeta
> `incoming/<slug>/`, *Add file → Upload files*, arrossega els fitxers i fes
> commit a la branca.

#### Opció B — Local (al teu ordinador)

```bash
pip install cloudinary

CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name> \
    python3 tools/build_playlist.py <slug> --title "Títol visible de la llista"
```

Opcions:

- `--front`: afegeix el slug a dalt de `index.json` en comptes del final.

Després fes commit de `playlists/<slug>.json` i `playlists/index.json`.

### Pas 5 — Comprova-ho

Serveix el web localment (secció 2) i obre el selector: la llista nova hi ha de
sortir. Entra-hi i comprova que les cançons es reprodueixen i que la lletra es
mostra (karaoke si hi havia `.lrc`).

---

## 4. Credencials de Cloudinary

- **Mai** al repositori. Es passen com a variables d'entorn:
  - En **GitHub Actions**: com a *secrets* del repo (Opció A).
  - En **local**: com a variable `CLOUDINARY_URL` (o bé `CLOUDINARY_API_KEY` +
    `CLOUDINARY_API_SECRET` + `CLOUDINARY_CLOUD_NAME`) a la teva sessió.
- Els `.m4a` són pesats: un cop pujats a Cloudinary, convé **esborrar-los de
  `incoming/`** perquè no engreixin l'historial del repo (les URLs ja apunten a
  Cloudinary).

---

## 5. Resolució de problemes

| Símptoma | Causa probable |
|---|---|
| El selector es queda a "Carregant…" | Has obert el fitxer amb `file://`. Fes servir un servidor local (secció 2). |
| Una cançó surt en gris i no s'hi pot clicar | No tenia fitxer d'àudio (`.m4a`/`.mp4`) amb el número correcte. |
| No es veu la lletra sincronitzada | Falta el `.lrc` o el seu número no coincideix amb el de la cançó. |
| La llista nova no surt al selector | El slug no s'ha afegit a `playlists/index.json` (revisa el pas de generació). |
| El workflow falla | Falten els secrets de Cloudinary, o el `manifest.csv` no és a `incoming/<slug>/`. |
