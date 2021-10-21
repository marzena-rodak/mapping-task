# mapping-task
Download and process articles from certain API

To run the printe use following code. First result will 
be visible after 5 minutes.

```
from article_printer import ArticlePrinter

art = ArticlePrinter()
art.run()
```

To see the results faster you can change the interval
between executions by passing number of minutes to `art.run`:

```
art.run(1)
```
