<p align='center'>
  <a href='https://praig.ua.es/'><img src='https://i.imgur.com/Iu7CvC1.png' alt='PRAIG-logo' width='100'></a>
</p>

<h1 align='center'>Completing Music Notation Datasets for
Multimodal Learning</h1>


<p align='center'>
  <a href='#about'>About</a> •
  <a href='#how-to-use'>How To Use</a> •
  <a href='#citations'>Citations</a> •
  <a href='#acknowledgments'>Acknowledgments</a> •
  <a href='#references'>References</a>
</p>

## About

This repository provides tools and utilities to pre-process:

- **TriScore**: Built from the excerpt-level MUSCUTS subset of MUSCAT [1]. The original MUSCUTS collection provides real audio excerpts and aligned symbolic scores in kern, but it does not provide score images cropped or rendered at the same excerpt level. To complete the triplets, each kern fragment is rendered as a sheet-music image using the [Verovio toolkit](https://book.verovio.org/installing-or-building-from-sources/python.html). Metadata is recovered from the MUSCAT database, including composer, instrument, and piece title annotations. The resulting collection contains aligned audio–image–symbolic triplets and metadata for multimodal classification or retrieval. The dataset is available upon request [here](https://grfia.dlsi.ua.es/muscat/). 

- **MTD-kern** [2]: the Musical Theme Dataset [2] contains real audio, score images, symbolic representations, and metadata. However, its symbolic material is distributed mainly in MusicXML rather than in kern. We therefore convert the MusicXML files to kern using [humlib](https://humlib.humdrum.org/). This normalization step makes MTD compatible with the same symbolic-processing pipeline used for TriScore and allows the dataset to be incorporated into a common multimodal experimental framework. The available metadata supports composer, ensemble, instrument, and polyphony-related labels. The dataset is open to download [here](https://www.audiolabs-erlangen.de/resources/MIR/MTD). 

- **Primus Extended** [3]: PriMus consists of monophonic incipits retrieved from the [RISM (Répertoire International des Sources Musicales)](https://rism.info/)  collection. A multimodal version was originally constructed for multimodal transcription [3]. Since the original dataset does not directly provide the metadata required for classification or retrieval, we query the [RISM API](https://rism.online/docs/api/api/) using the samples identifiers to recover labels such as author, title, and genre/subject. Dataset available upon request.


## How To Use

**Script**: `main.py`

**Arguments**: 

- `--ds_name`: The name of the dataset, either `triscore`, `primus` or `mtd`.
- `--ds_dir`: The folder containing data. I suggest this structure, passing the directory for each of the datasets (`./data/MUSCUTS` for `TriScore`; `./data/MTD` for `MTD-kern`; and `./data/Primus` for `Primus Extended` )
  ```
    data
    ├───MTD
    │   ├───data_SCORE_IMG
    │   ├───data_SCORE_XML
    │   └───other_FORMATS
    ├───MUSCUTS
    │   ├───Abel_Moreno
    │   │   └───La_Madruga
    │   └───Other_Composers
    │       └───Other_pieces
    └───Primus
        ├───230006606-1_3_2
        └───other ids
  ```

- `--log_dir`: Folder to log if any errors occur (`/log`).

The dependencies are specified in the [`Dockerfile`](Dockerfile) (recommended) and [`requirements.txt`](requirements.txt). If not able to use a dockerfile, make sure that the necessary libraries are installed and built, (`humlib`, `humextra` and `python` requirements) as follows:

```
git clone https://github.com/craigsapp/humextra && \
cd humextra && \
make && \
make pae2kern
git clone https://github.com/humdrum-tools/humlib && \
    cd humlib && \
    make
pip install -r requirements.txt
```

## Citations

```bibtex
@article{HIDALGO2026_TRISCORE,
  title = {TriScore: Aligning audio, symbolic scores, and sheet music images in a shared embedding space},
  journal = {Pattern Recognition},
  volume = {179},
  pages = {113926},
  year = {2026},
  issn = {0031-3203},
  doi = {https://doi.org/10.1016/j.patcog.2026.113926},
  url = {https://www.sciencedirect.com/science/article/pii/S0031320326008915},
  author = {Antonio Hidalgo-Centeno and Eliseo Fuentes-Martinez and Jorge Calvo-Zaragoza and Antonio Javier Gallego},
  keywords = {Multimodal music classification, Cross-modal representation learning, Music Information Retrieval, Audio-score-image alignment, Benchmark dataset},
}
```

## Acknowledgments

This research was supported by the Spanish Ministry of Science and Innovation through the LEMUR research project (PID2023-148259NB-I00), funded by MCIU/AEI/10.13039/501100011033/FEDER, EU, and the European Social Fund Plus (FSE+).

<p align="center">
    <a href="https://praig.ua.es/category/research/projects/"><img src="https://raw.githubusercontent.com/lemur-project/acknowledgments/refs/heads/main/infographics/lemur_logo.png" alt="LEMUR logo" height="60"></a>
    <a href="https://www.aei.gob.es/"><img src="https://raw.githubusercontent.com/lemur-project/acknowledgments/refs/heads/main/infographics/acknowledgements.png" alt="Ministry Logo, European Union Flag and Statal Research Agency Logo" height="60"></a>
    <br>
</p>

## References

[1] A. Galan-Cuenca, J. J. Valero-Mas, J. C. Martinez-Sevilla, A. Hidalgo-Centeno, A. Pertusa, and J. Calvo-Zaragoza, “MUSCAT: A multimodal mUSic collection for automatic transcription of real recordings and image scores,” in Proc. 32nd ACM Int. Conf. Multimedia (MM ’24), New York, NY, USA: Association for Computing Machinery, 2024, pp. 583–591, doi: 10.1145/3664647.3681572.

[2] F. Zalkow, S. Balke, V. Arifi-Müllerand M. Müller, “MTD: A Multimodal Dataset of Musical Themes for MIR Research”, Transactions of the International Society for Music Information Retrieval, vol. 3, no. 1, p. 180–192, 2020, doi: 10.5334/tismir.68.

[3] . Alfaro-Contreras, J. J. Valero-Mas, J. M. Iñesta, and J. Calvo-Zaragoza, “Late multimodal fusion for image and audio music transcription,” Expert Syst. Appl., vol. 216, Apr. 2023, Art. no. 119491, doi: 10.1016/j.eswa.2022.119491.