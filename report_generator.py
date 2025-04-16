from fpdf import FPDF
import pandas as pd
from transformers import pipeline
import os
import logging
from translate import Translator
from email_sender import send_email

class ReportGenerator:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_dir = config['report']['output_dir']
        os.makedirs(self.output_dir, exist_ok=True)
        self.nlp = pipeline("text-generation", model="gpt2")
        self.translator = Translator(to_lang=config['report']['language'])

    def generate_report(self, data, stats, forecasts):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Title
            pdf.cell(200, 10, txt="Advanced Sales Data Report", ln=True, align='C')

            # NLP Insights
            insights = self.nlp(f"Sales data summary: mean {stats['mean']:.2f}, median {stats['median']:.2f}.")[0]['generated_text']
            translated_insights = self.translator.translate(insights)
            pdf.ln(10)
            pdf.multi_cell(0, 10, translated_insights)

            # Visualizations
            viz_dir = self.config['visualization']['output_dir']
            for viz in ['sales_over_time.png', 'top_products.png']:
                pdf.ln(10)
                pdf.image(os.path.join(viz_dir, viz), x=10, w=190)

            # Save report
            output_path = os.path.join(self.output_dir, f'sales_report_{self.config["report"]["language"]}.pdf')
            pdf.output(output_path)
            self.logger.info(f"Saved report to {output_path}")

            # Send report via email
            send_email(
                self.config['email']['smtp_server'],
                self.config['email']['smtp_port'],
                self.config['email']['sender'],
                self.config['email']['password'],
                self.config['email']['recipients'],
                "Sales Data Report",
                "Attached is the latest sales data report.",
                [output_path]
            )
            self.logger.info("Sent report via email")

        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            raise