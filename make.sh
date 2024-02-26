#!/bin/zsh
source /Users/tremus/anaconda3/etc/profile.d/conda.sh
conda activate trbase

python3 -m build
pip install .

## Spread the word
#conda activate techExploration
#pip install .
#conda activate trfindev
#pip install .
#conda activate trnotes
#pip install .
#conda activate zweiundvierzig
#pip install .
#conda activate gemini
#pip install .
#conda activate llmautocomplete
#pip install .
#conda activate llmautocomplete310
#pip install .
#conda activate trbase


