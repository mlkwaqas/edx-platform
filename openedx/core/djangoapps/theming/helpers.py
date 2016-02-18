"""
    Helpers for accessing comprehensive theming related variables.
"""
import os.path
from path import Path

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache

from microsite_configuration import microsite
from microsite_configuration import page_title_breadcrumbs


def get_page_title_breadcrumbs(*args):
    """
    This is a proxy function to hide microsite_configuration behind comprehensive theming.
    """
    return page_title_breadcrumbs(*args)


def get_value(val_name, default=None, **kwargs):
    """
    This is a proxy function to hide microsite_configuration behind comprehensive theming.
    """
    return microsite.get_value(val_name, default=default, **kwargs)


def get_template_path(relative_path, **kwargs):
    """
    This is a proxy function to hide microsite_configuration behind comprehensive theming.
    """
    return microsite.get_template_path(relative_path, **kwargs)


def is_request_in_themed_site():
    """
    This is a proxy function to hide microsite_configuration behind comprehensive theming.
    """
    return microsite.is_request_in_microsite()


def get_template(uri):
    """
    This is a proxy function to hide microsite_configuration behind comprehensive theming.
    :param uri: uri of the template
    """
    return microsite.get_template(uri)


def get_themed_template_path(relative_path, default_path, **kwargs):
    """
    This is a proxy function to hide microsite_configuration behind comprehensive theming.

    The workflow considers the "Stanford theming" feature alongside of microsites.  It returns
    the path of the themed template (i.e. relative_path) if Stanford theming is enabled AND
    microsite theming is disabled, otherwise it will return the path of either the microsite
    override template or the base lms template.

    :param relative_path: relative path of themed template
    :param default_path: relative path of the microsite's or lms template to use if
        theming is disabled or microsite is enabled
    """
    is_stanford_theming_enabled = settings.FEATURES.get("USE_CUSTOM_THEME", False)
    is_microsite = microsite.is_request_in_microsite()
    if is_stanford_theming_enabled and not is_microsite:
        return relative_path
    return microsite.get_template_path(default_path, **kwargs)


def get_template_path_in_theme(relative_path):
    """
    Returns template path in current site's theme if it finds one there otherwise returns same path.
    :param relative_path:
    :return: template path in current site's theme
    """
    site_theme_dir = get_current_site_theme_dir()
    if not site_theme_dir:
        return relative_path

    root_name = get_project_root_name()
    base_theme_dir = get_base_theme_dir()
    template_path = "/".join([
        base_theme_dir,
        site_theme_dir,
        root_name,
        "templates"
    ])

    # strip `/` if present at the start of relative_path
    template_name = relative_path[1:] if relative_path.startswith('/') else relative_path
    search_path = os.path.join(template_path, template_name)
    if os.path.isfile(search_path):
        path = '/{site_theme_dir}/{root_name}/templates/{template_name}'.format(
            site_theme_dir=site_theme_dir,
            root_name=root_name,
            template_name=template_name,
        )
        return path
    else:
        return relative_path


def get_current_site_theme_dir():
    """
    :return: theme directory for current site
    """
    from edxmako.middleware import REQUEST_CONTEXT
    request = getattr(REQUEST_CONTEXT, 'request', None)
    if not request:
        return None

    site = get_current_site(request)
    site_theme_dir = cache.get(get_site_theme_cache_key(site))

    # if site theme dir is not in cache and comprehensive theming is enabled then pull it from db.
    if not site_theme_dir and is_comprehensive_theming_enabled():
        site_theme = site.themes.first()
        if site_theme:
            site_theme_dir = site_theme.theme_dir_name
            cache_site_theme_dir(site, site_theme_dir)
    return site_theme_dir


def get_project_root_name():
    """
    :return: component name of platform e.g lms, cms
    """

    root = Path(settings.PROJECT_ROOT)
    if root.name == "":
        root = root.parent
    return root.name


def get_base_theme_dir():
    """
    :return: Base theme directory
    """
    return settings.COMPREHENSIVE_THEME_DIR


def is_comprehensive_theming_enabled():
    """
    :return boolen: boolean indicating of comprehensive theming is enabled or not
    """
    return True if settings.COMPREHENSIVE_THEME_DIR else False


def get_site_theme_cache_key(site):
    """
    :param site: site where key needs to generated
    :return: a key to be used a cache key
    """
    cache_key = "theming.site.{domain}".format(
        domain=site.domain
    )
    return cache_key


def cache_site_theme_dir(site, theme_dir):
    """
    Cache site's theme directory.
    :param site:
    :param theme_dir:
    """
    cache.set(get_site_theme_cache_key(site), theme_dir, settings.FOOTER_CACHE_TIMEOUT)
