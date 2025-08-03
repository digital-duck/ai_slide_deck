# AI Slides

## GLM 4.5 by ZhiPu

- https://chat.z.ai/c/356232ba-5516-46b6-96aa-37128dd14364


### Prompt
```
I like to use prefect python dynamic workflow library, 

can you create a slide deck on its capability, quick setup, application, comparison with similar tool?

make first 10 slides as main content to be presented

All additional slides under Appendix section

Use HTML for each page

```


```bash

# gen HTML
python slide_generator.py generate -d "prefect_slides" -t "Prefect" -o index_prefect.html

# gen PDF
python slide_generator.py generate-pdf -d prefect_slides -m weasyprint -t "Prefect" -o prefect_gen.pdf

```