.PHONY: clean cleanall
report.pdf: $(wildcard *.tex) $(wildcard *.cls) $(wildcard figures/*.eps)
	latexmk -pdf -interaction=nonstopmode report.tex
clean:
	latexmk -c
cleanall:
	latexmk -c
	rm -f report.pdf
figures/%.eps: figures/%.dot
	dot -Teps $< -o $@
