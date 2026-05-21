# Targets:
#   make setup      install Python dependencies
#   make pipeline   run the full analysis end-to-end
#   make dashboard  start the local Streamlit dashboard
#   make clean      delete the generated database and outputs

.PHONY: setup pipeline dashboard

setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py
	python analysis/frequencies.py
	python analysis/responders.py
	python analysis/baseline.py

dashboard:
	python -m streamlit run dashboard/app.py

clean:
	rm -f loblaw.db
	rm -rf outputs/