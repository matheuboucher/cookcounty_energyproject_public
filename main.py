from dash import Dash
from dash_bootstrap_components.themes import BOOTSTRAP
from src.components.layout.layout import create_layout

def main() -> None:
    """ Main method """
    app = Dash(external_stylesheets=[BOOTSTRAP])
    app.title = "Cook County Energy Data and Projections"
    app.layout = create_layout(app)
    app.run_server(debug=True)

if __name__ == "__main__":
    main()
