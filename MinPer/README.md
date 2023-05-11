## Folder Structure

```
├── README.md
├── INSTALL.md
├── src
│   ├── Phase1 - TAIFU: link here
│   │ 
│   ├── Phase2
│   │	├── permission_ana.py
│   │   ├── sentence_perm_classifier.py
│   │
│   ├── Phase3
│       ├── nn_overclaim_det.py
│       ├── verb_overclaim_det.py
│       ├── same_group_det.py
├── dataset
│	├── channel_api_nn.txt
│ 
├── stanford_parser
│   ├── atomic_operation.py
│   ├── load_finfo.py
│   ├── stanford_parser.py


```


## Description:
Our source data is already stored in folder dataset, if user would like to fetch data from original: please refer to TAIFU paper, and we start directly from Phase2

### Phase 2:
```permission_ana.py```: Run this file to obtain the full outputs on the console. This corresponds to the Section V.A permission S of our paper.

```sentence_perm_classifier.py```  This corresponds to the Section V.A Permission R of our paper.

We put the Section V.B part into folder ```stanford_parser``` since it is heavily used by other parts. 
<li> For complex permission splitation, refer to function ```atomic_sentence``` stored in ```atomic_operation.py```. </li>
<li> For verb, noun extraction, refer to ```stanford_parser.py``` </li> 

### Phase 3: 
As mentioned in our paper, we would first check noun permission excess, then verb permission excess, we also explore the group level permission excess. As demonstrated by the name of ```nn_overclaim_det.py```,  ```verb_overclaim_det.py``` and ```same_group_det.py```


