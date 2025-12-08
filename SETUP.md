# Installation

## 1. Project Dependencies
First, clone the project through:
```bash
git clone https://github.com/Ar-temis/Course-Recommendation.git
cd Course-Recommendation
```

I recommend making a virtual environment and downloading the dependencies.

> [!NOTE]
> Every command here is executed in the project root folder.

I have used `uv` for this and I recommend using `uv` to install everything.
You can install it using PyPI:
```bash
pip install uv
``` 

With `uv`, you can create virtual environments using:
```bash
uv venv --python 3.11
```

Then source your environment through:
```bash
# On mac and linux
source .venv/bin/activate
```

Now, we are ready to install the project dependencies.
`uv` makes it very easy with the following command:
```bash
uv sync
```

## 2. Ollama
The other major dependency you need to install is **Ollama**.
Please look into their [download page](https://ollama.com/download) for instructions.

Right now, I am using [gpt-oss:20b](https://ollama.com/library/gpt-oss) as my LLM in the cloud and [embeddinggemma](https://huggingface.co/google/embeddinggemma-300m) as my embedding model.

### GPT-OSS
> [!IMPORTANT]
> You have to create ollama account for gpt-oss to work. Please follow their [instructions](https://docs.ollama.com/cloud#python).

Once you have created your API key, put it in the `.env` file at `Course-Recommendation/crec/.env`.

It should look like so:
```env
API_KEY="{api_key without the curly brackets}"
```

Then, you should pull the `gpt-oss` model with:
```bash
ollama pull gpt-oss:20b-cloud
```

### embeddinggemma
You should run the following command to install `embeddinggemma`:
```bash
ollama pull embeddinggemma:300m
```

I ran the embedding model on my laptop with the following specs:
```bash
> fastfetch
             .',;::::;,'.                 artemis@fedora
         .';:cccccccccccc:;,.             --------------
      .;cccccccccccccccccccccc;.          OS: Fedora Linux 43 (KDE Plasma Desktop Edition) x86_64
    .:cccccccccccccccccccccccccc:.        Host: ROG Strix G733ZW_G733ZW (1.0)
  .;ccccccccccccc;.:dddl:.;ccccccc;.      Kernel: Linux 6.17.9-300.fc43.x86_64
 .:ccccccccccccc;OWMKOOXMWd;ccccccc:.     Uptime: 29 mins
.:ccccccccccccc;KMMc;cc;xMMc;ccccccc:.    Packages: 3031 (rpm), 19 (snap)
,cccccccccccccc;MMM.;cc;;WW:;cccccccc,    Shell: zsh 5.9
:cccccccccccccc;MMM.;cccccccccccccccc:    Display (BOE0A69): 2560x1440 @ 240 Hz (as 2048x1152) in 17" [Built-in]
:ccccccc;oxOOOo;MMM000k.;cccccccccccc:    DE: KDE Plasma 6.5.3
cccccc;0MMKxdd:;MMMkddc.;cccccccccccc;    WM: KWin (Wayland)
ccccc;XMO';cccc;MMM.;cccccccccccccccc'    WM Theme: Breeze
ccccc;MMo;ccccc;MMW.;ccccccccccccccc;     Theme: Breeze (Dark) [Qt], Breeze [GTK3]
ccccc;0MNc.ccc.xMMd;ccccccccccccccc;      Icons: YAMIS [Qt], YAMIS [GTK3/4]
cccccc;dNMWXXXWM0:;cccccccccccccc:,       Font: JetBrainsMono Nerd Font (10pt) [Qt], JetBrainsMono Nerd Font (10pt) [GTK3/4]
cccccccc;.:odl:.;cccccccccccccc:,.        Cursor: breeze (24px)
ccccccccccccccccccccccccccccc:'.          Terminal: kitty 0.43.1
:ccccccccccccccccccccccc:;,..             Terminal Font: JetBrainsMonoNFM-Regular (13pt)
 ':cccccccccccccccc::;,.                  CPU: 12th Gen Intel(R) Core(TM) i9-12900H (14) @ 5.00 GHz
                                          GPU 1: NVIDIA Geforce RTX 3070 Ti Laptop GPU 8GB [Discrete]
                                          GPU 2: Intel Iris Xe Graphics @ 1.45 GHz [Integrated]
                                          Memory: 6.90 GiB / 31.00 GiB (22%)
                                          Swap: 0 B / 8.00 GiB (0%)
                                          Disk (/): 163.66 GiB / 268.69 GiB (61%) - btrfs
                                          Local IP (wlo1): 172.28.31.253/16
                                          Battery (GA50358): 100% [AC Connected]
                                          Locale: en_US.UTF-8
```

### Model Changing
If you want to use smaller models, you can look through this [website](https://ollama.com/library). 
Then, you should pull the model like we did for `embeddinggemma`above.

You can change models in this file, in here:

https://github.com/Ar-temis/Course-Recommendation/blob/0c03bfcd448c4d0ebcdf9a059b290c3e3381b4b2/crec/config.py#L50-L57

## 3. Downloading necessary data

Download the data necessary from this [link](https://duke.box.com/s/0db37aeh6ott2wiaq2wdfyc4m2t7rt9x). 
Once downloaded, put it in the project root folder so that the structure looks like this:
```
Course-Recommendation
├── app
├── crec
├── data
├── dbs
├── LICENSE
├── pyproject.toml
├── README.md
├── SETUP.md
└── tests
```

## 4. Running the installation script

You can run the installation script with:
```bash
python3 crec/setup.py
```
---

# Congratulations
You have set up all the necessary dependencies for this project. Head on back to [README](https://github.com/Ar-temis/Course-Recommendation/tree/main#readme) for instructions on running this project. 
