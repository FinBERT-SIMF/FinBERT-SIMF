import  dash
from flask.helpers import get_root_path
from app.dashbards.dashapp1.layout import  layout as layout1
from app.dashbards.dashapp1.callbacks import register_callbacks as register_callbacks1
from app.dashbards.dashapp2.layout import  layout as layout2
from app.dashbards.dashapp2.callback import register_callbacks as register_callbacks2





def register_dashapp(app, title, base_pathname, layout, register_callbacks_fun):
    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    my_dashapp = dash.Dash(__name__,
                           server=app,
                           url_base_pathname=f'/{base_pathname}/',
                           assets_folder=get_root_path(__name__) + f'/{base_pathname}/assets/',
                           meta_tags=[meta_viewport])

    with app.app_context():
        my_dashapp.title = title
        my_dashapp.layout = layout
        register_callbacks_fun(my_dashapp)
    #_protect_dashviews(my_dashapp)

# simply add new dash template in this function
def init_dashRoutes(app):
    register_dashapp(app, 'Dashapp 1', 'dashboard1', layout1, register_callbacks1)
    register_dashapp(app, 'Dashapp 2', 'dashboard2', layout2, register_callbacks2)


