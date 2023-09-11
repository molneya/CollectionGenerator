# Collection Generator

A program to generate and manage osu! collections.

## Setup

For Windows, download and run the latest version from [releases](https://github.com/molneya/CollectionGenerator/releases).

Otherwise, clone and run the code using:
```bash
git clone https://github.com/molneya/CollectionGenerator
cd CollectionGenerator
python main.py
```

### First Run

When running for the first time, you'll need to edit your configuration to specify your osu! directory and osu!api credentials. Do so by selecting `Config` in the menu, then pressing the `Save and Reload` button to save your desired changes. You can use the program without doing this, but functionality will be limited.

## Usage

### Loading and Saving Collections

You can load collections in either `.db` or `.osdb` format by selecting `File > Open > File`. A shortcut for opening your osu! collection directly exists by selecting `File > Open > osu! Collection`. Alternatively, you can drag and drop your collections into the program.

You can also save collections in a similar manner by selecting `File > Save`. Right-clicking a collection in the list and selecting `Save` saves the collection on its own.

Read more about the difference in osu! collection formats [here](https://github.com/Piotrekol/CollectionManager#collection-file-formats).

### Generating Collections

The `Generate` menu dropdown has many selections to generate collections with certain specifications:
- `Bests` generates collections of a user's top 100 best pp plays.
- `Filter > Beatmaps` generates collections using beatmap filters.
- `Filter > Scores` generates collections using score filters.
- `Firsts > Country` generates collections of the user's country first places.
- `Firsts > Global` generates collections of the user's global first places.
- `Leaderboards` generates collections of the user's specified ranks on the global leaderboard.
- `Leeways` generates collections of beatmap spinner leeways.

### Editing Collections

Right-click a collection in the collection list to see possible collection operations:
- `Delete` removes the collection from the list.
- `Duplicate` creates a copy of the collection.
- `Invert` creates a collection containing all maps in your database without the ones present the selected collection.
- `Subtract` creates a copy of the selected collection without the beatmaps of the subtracted collection.

Selecting and right-clicking multiple collections in the collection list shows yet more possible operations:
- `Merge` creates a new collection containing all beatmaps of the selected collections.
- `Intersect` creates a new collection containing all the common beatmaps of the selected collection.

Double-clicking a collection also allows you to rename it.

There exists no method for editing individual beatmaps in collections. If this is what you want to do, I recommend using [Piotrekol's Collection Manager](https://github.com/Piotrekol/CollectionManager) instead.
