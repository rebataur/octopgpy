from datetime import datetime

from lona.html import HTML, H1, Div
from lona import LonaApp, LonaView
from lona.html import HTML, TextInput, Button
from lona import LonaView
app = LonaApp(__file__)


@app.route('/')
class ClockView(LonaView):
    def handle_request(self, request):
        timestamp = Div()
        text_input = TextInput(value="test", bubble_up=False)
        html = HTML(
            H1('Clock'),
            timestamp,
            text_input
        )

        while True:
            timestamp.set_text(str(datetime.now()))

            self.show(html)

            self.sleep(1)


app.run(port=8080)