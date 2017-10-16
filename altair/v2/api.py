"""
Main API for Vega-lite spec generation.

DSL mapping Vega types to IPython traitlets.
"""
import os
import functools
import operator
import uuid
import warnings

import traitlets as T
import pandas as pd

from ..utils import node, create_vegalite_mime_bundle
from ..utils._py3k_compat import string_types
from .traitlet_utils import update_subtraits

from .. import expr
from . import schema

from .schema import jstraitlets as jst

from .schema import (
    AggregateOp,
    AndFilter,
    Axis,
    AxisConfig,
    AxisConfigMixins,
    AxisEncoding,
    AxisOrient,
    BOXPLOT,
    BarConfig,
    BaseBin,
    BaseSelectionDef,
    BaseSpec,
    Bin,
    BinTransform,
    BoxPlotConfig,
    BoxPlotConfigMixins,
    BoxPlotDef,
    BrushConfig,
    CalculateTransform,
    CellConfig,
    CompositeMarkConfigMixins,
    CompositeMarkDef,
    CompositeUnitSpec,
    CompositeUnitSpecAlias,
    ConditionLegendFieldDef,
    ConditionNumberValueDef,
    ConditionOnlyNumberLegendDef,
    ConditionOnlyStringLegendDef,
    ConditionOnlyTextDef,
    ConditionStringValueDef,
    ConditionTextFieldDef,
    ConditionTextValueDef,
    ConditionalNumberLegendDef,
    ConditionalNumberLegendFieldDef,
    ConditionalNumberLegendValueDef,
    ConditionalStringLegendDef,
    ConditionalStringLegendFieldDef,
    ConditionalStringLegendValueDef,
    ConditionalTextDef,
    ConditionalTextFieldDef,
    ConditionalTextValueDef,
    Config,
    Data,
    DataFormat,
    DataFormatType,
    DataUrlFormat,
    DateTime,
    ERRORBAR,
    Encoding,
    EncodingWithFacet,
    EqualFilter,
    ExtendedScheme,
    Facet,
    FacetFieldDef,
    FacetedCompositeUnitSpecAlias,
    FacetedSpec,
    FacetedUnitSpec,
    FieldDef,
    FieldDefBase,
    FilterTransform,
    FontStyle,
    FontWeight,
    Guide,
    GuideEncodingEntry,
    HConcatSpec,
    Header,
    HorizontalAlign,
    InlineData,
    Interpolate,
    IntervalSelection,
    IntervalSelectionConfig,
    LayerSpec,
    LayoutSizeMixins,
    Legend,
    LegendConfig,
    LegendEncoding,
    LegendFieldDef,
    LegendOrient,
    LookupData,
    LookupTransform,
    Mark,
    MarkConfig,
    MarkConfigMixins,
    MarkDef,
    MultiSelection,
    MultiSelectionConfig,
    NamedData,
    NonspatialResolve,
    NotFilter,
    NumberValueDef,
    OneOfFilter,
    OrFilter,
    OrderFieldDef,
    Orient,
    PositionFieldDef,
    RangeFilter,
    Repeat,
    RepeatRef,
    RepeatSpec,
    ResolveMapping,
    ResolveMode,
    Root,
    Scale,
    ScaleConfig,
    ScaleFieldDef,
    ScaleType,
    SelectionAnd,
    SelectionConfig,
    SelectionDef,
    SelectionDomain,
    SelectionFilter,
    SelectionNot,
    SelectionOr,
    SelectionResolution,
    SingleDefChannel,
    SingleSelection,
    SingleSelectionConfig,
    SortField,
    SpatialResolve,
    Spec,
    StackOffset,
    StringValueDef,
    Summarize,
    SummarizeTransform,
    TextConfig,
    TextFieldDef,
    TextValueDef,
    TickConfig,
    TimeUnit,
    TimeUnitTransform,
    TopLevelExtendedSpec,
    TopLevelFacetedSpec,
    TopLevelFacetedUnitSpec,
    TopLevelHConcatSpec,
    TopLevelLayerSpec,
    TopLevelProperties,
    TopLevelRepeatSpec,
    TopLevelVConcatSpec,
    Transform,
    Type,
    UrlData,
    VConcatSpec,
    VLOnlyConfig,
    ValueDef,
    VerticalAlign,
    VgAxisBase,
    VgAxisConfig,
    VgBinding,
    VgCheckboxBinding,
    VgGenericBinding,
    VgLegendBase,
    VgLegendConfig,
    VgMarkConfig,
    VgRadioBinding,
    VgRangeBinding,
    VgRangeScheme,
    VgSelectBinding,
    VgTitleConfig,
    VlOnlyGuideConfig,
)


class MaxRowsExceeded(Exception):
    """Raised if the number of rows in the dataset is too large."""
    pass

DEFAULT_MAX_ROWS = 5000

#*************************************************************************
# Rendering configuration
#*************************************************************************

# This is added to TopLevelMixin as a method if MIME rendering is enabled
def _repr_mimebundle_(self, include, exclude, **kwargs):
    """Return a MIME-bundle for rich display in the Jupyter Notebook."""
    spec = self.to_dict()
    bundle = create_vegalite_mime_bundle(spec)
    return bundle


def enable_mime_rendering():
    """Enable MIME bundle based rendering used in JupyterLab/nteract."""
    # This is what makes Python fun!
    delattr(TopLevelMixin, '_ipython_display_')
    TopLevelMixin._repr_mimebundle_ = _repr_mimebundle_

#*************************************************************************
# Channel Aliases
#*************************************************************************
from .schema import (Color, Column, Detail, Opacity, Order, Row,
                     Shape, Size, Text, Tooltip, X, X2, Y, Y2)
from .schema import Encoding, EncodingWithFacet, Facet


def use_signature(Obj):
    """Apply call signature and documentation of Obj to the decorated method"""
    def decorate(f):
        # call-signature of f is exposed via __wrapped__.
        # we want it to mimic Obj.__init__
        f.__wrapped__ = Obj.__init__
        f._uses_signature = Obj

        # Supplement the docstring of f with information from Obj
        f.__doc__ += Obj.__doc__[Obj.__doc__.index('\n'):]
        return f
    return decorate


#*************************************************************************
# CalculateTransform wrapper
# - makes field a required first argument of initialization
# - allows expr trait to be an Expression and processes it properly
#*************************************************************************
class CalculateTransform(schema.CalculateTransform):
    calculate = jst.JSONUnion([jst.JSONString(),
                               jst.JSONInstance(expr.Expression)],
                               help=schema.CalculateTransform.calculate.help)

    def __init__(self, as_, calculate=jst.undefined, **kwargs):
        super(CalculateTransform, self).__init__(as_=as_, calculate=calculate, **kwargs)

    def _finalize(self, **kwargs):
        """Finalize object: convert expr expression to string if necessary"""
        if isinstance(self.calculate, expr.Expression):
            self.calculate = repr(self.calculate)
        super(CalculateTransform, self)._finalize(**kwargs)


#*************************************************************************
# FilterTransform wrapper
# - allows filter trait to be an Expression and processes it properly
#*************************************************************************
class FilterTransform(schema.FilterTransform):
    filter = jst.JSONUnion([jst.JSONString(),
                            jst.JSONInstance(expr.Expression),
                            jst.JSONInstance(schema.EqualFilter),
                            jst.JSONInstance(schema.RangeFilter),
                            jst.JSONInstance(schema.OneOfFilter),
                            jst.JSONArray(jst.JSONUnion([
                                jst.JSONString(),
                                jst.JSONInstance(expr.Expression),
                                jst.JSONInstance(schema.EqualFilter),
                                jst.JSONInstance(schema.RangeFilter),
                                jst.JSONInstance(schema.OneOfFilter)]))],
                           help=schema.FilterTransform.filter.help)

    def _finalize(self, **kwargs):
        """Finalize object: convert filter expressions to string"""
        convert = lambda f: repr(f) if isinstance(f, expr.Expression) else f
        self.filter = convert(self.filter)
        if isinstance(self.filter, list):
            self.filter = [convert(f) for f in self.filter]
        super(Transform, self)._finalize(**kwargs)


#*************************************************************************
# Top-level Objects
#*************************************************************************
class TopLevelMixin(object):

    @staticmethod
    def _png_output_available():
        return node.vl_cmd_available('vl2png')

    @staticmethod
    def _svg_output_available():
        return node.vl_cmd_available('vl2svg')

    def savechart(self, outfile, filetype=None):
        """Save a chart to file, in either png, svg, json, or html format.

        Note that png/svg output requires several nodejs packages to be
        installed and correctly configured. Before running this, you must
        have nodejs and cairo on your system and use the node package manager
        to install the ``canvas`` and ``vega-lite`` packages.

        If you are using anaconda, you can set it up this way:

            $ conda create -n node-env -c conda-forge python=2.7 cairo nodejs altair
            $ source activate node-env
            $ npm install canvas vega-lite

        The node binaries used here (``vl2vg``, ``vl2png``, ``vl2svg``) will be
        installed in the node root directory, which should be automatically
        detected by this function.

        Parameters
        ----------
        outfile : str
            The output filename
        filetype : str (optional)
            The filetype to use. One of ('svg', 'png', 'json', 'html').
            If not specified, it will be inferred from outfile.
        """
        if filetype is None:
            try:
                base, ext = os.path.splitext(outfile)
                filetype = ext[1:]
            except AttributeError:
                raise ValueError('filetype could not be inferred')

        if filetype in node.SUPPORTED_FILETYPES:
            node.savechart(self, outfile, filetype)
        elif filetype == 'json':
            if hasattr(outfile, 'write'):
                outfile.write(self.to_json())
            else:
                with open(outfile, 'w') as f:
                    f.write(self.to_json())
        elif filetype == 'html':
            if hasattr(outfile, 'write'):
                outfile.write(self.to_html())
            else:
                with open(outfile, 'w') as f:
                    f.write(self.to_html())
        else:
            supported = node.SUPPORTED_FILETYPES + ['json', 'html']
            raise ValueError('Cannot save chart of type {0}; supported'
                             'extensions are {1}'.format(filetype, supported))

    def to_html(self, template=None, title=None, **kwargs):
        """Emit a stand-alone HTML document containing this chart.

        Parameters
        ----------
        template : string
            The HTML template to use. This should have a format method, which
            accepts a "spec" and "title" argument. Note that a standard Python
            format string meets these requirements.
            By default, uses altair.utils.html.DEFAULT_TEMPLATE.
        title : string
            The title to use in the document. Default is "Vega-Lite Chart"
        kwargs :
            additional keywords to be passed to the template

        Returns
        -------
        html : string
            A string of HTML representing the chart

        See Also
        --------
        savechart : save a chart representation to file in various formats,
                    including HTML
        """
        from ..utils.html import to_html
        return to_html(self.to_dict(), template=template, title=title, **kwargs)

    def to_dict(self, data=True):
        """Emit the JSON representation for this object as as dict.

        Parameters
        ----------
        data : bool
            If True (default) then include data in the representation.

        Returns
        -------
        spec : dict
            The JSON specification of the chart object.
        """
        try:
            dct = super(TopLevelMixin, self).to_dict(data=data)
        except jst.UndefinedTraitError as err:
            # Suppress full traceback for clarity
            raise jst.UndefinedTraitError(str(err))
        dct['$schema'] = schema.vegalite_schema_url
        return dct

    @classmethod
    def from_dict(cls, dct):
        """Instantiate the object from a valid JSON dictionary

        Parameters
        ----------
        dct : dict
            The dictionary containing a valid JSON chart specification.

        Returns
        -------
        chart : Chart object
            The altair Chart object built from the specification.
        """
        if '$schema' in dct:
            if dct['$schema'] != schema.vegalite_schema_url:
                warnings.warn('from_dict: $schema={0} does not match '
                              'schema used to build this Altair version '
                              '({1}. '
                              ''.format(dct['$schema'],
                                        schema.vegalite_schema_url))
            dct = {k: v for k, v in dct.items() if k != '$schema'}
        return super(TopLevelMixin, cls).from_dict(dct)

    def to_json(self, data=True, sort_keys=True, **kwargs):
        """Emit the JSON representation for this object as a string.

        Parameters
        ----------
        data : bool
            If True (default) then include data in the representation.
        sort_keys : bool
            If True (default) then sort the keys in the output
        **kwargs
            Additional keyword arguments are passed to ``json.dumps()``

        Returns
        -------
        spec : string
            The JSON specification of the chart object.
        """
        kwargs['sort_keys'] = sort_keys
        try:
            json_output = super(TopLevelMixin, self).to_json(data=data,
                                                             json_kwds=kwargs)
        except jst.UndefinedTraitError as err:
            # Suppress full traceback for clarity
            raise jst.UndefinedTraitError(str(err))
        return json_output

    @classmethod
    def from_json(cls, json_string, **kwargs):
        """Instantiate the object from a valid JSON string

        Parameters
        ----------
        spec : string
            The string containing a valid JSON chart specification.

        Returns
        -------
        chart : Chart object
            The altair Chart object built from the specification.
        """
        return super(TopLevelMixin, cls).from_json(json_string,
                                                   json_kwds=kwargs)

    # TODO: Deprecate this
    def to_altair(self, data=None):
        """DEPRECATED. Use to_python() instead.

        Emit the Python code as a string required to created this Chart.
        """
        warnings.warn("to_altair() is deprecated. Use to_python() instead",
                      category=DeprecationWarning)
        return self.to_python(data=data)

    def to_python(self, data=None):
        """Emit the Python code as a string required to created this Chart."""
        try:
            python_output = super(TopLevelMixin, self).to_python(data=data)
        except jst.UndefinedTraitError as err:
            # Suppress full traceback for clarity
            raise jst.UndefinedTraitError(str(err))
        return python_output

    # Display related methods

    def _ipython_display_(self):
        """Use the vega package to display in the classic Jupyter Notebook."""
        from IPython.display import display
        from vega import VegaLite
        display(VegaLite(self.to_dict()))

    def display(self):
        """Display the Chart using the Jupyter Notebook's rich output.

        To use this is the classic Jupyter Notebook, the ``ipyvega`` package
        must be installed.

        To use this in JupyterLab/nteract, run the ``enable_mime_rendering``
        function first.
        """
        from IPython.display import display
        display(self)

    def serve(self, ip='127.0.0.1', port=8888, n_retries=50, files=None,
              jupyter_warning=True, open_browser=True, http_server=None,
              **html_kwargs):
        """Open a web browser and visualize the chart

        Parameters
        ----------
        html : string
            HTML to serve
        ip : string (default = '127.0.0.1')
            ip address at which the HTML will be served.
        port : int (default = 8888)
            the port at which to serve the HTML
        n_retries : int (default = 50)
            the number of nearby ports to search if the specified port
            is already in use.
        files : dictionary (optional)
            dictionary of extra content to serve
        jupyter_warning : bool (optional)
            if True (default), then print a warning if this is used
            within the Jupyter notebook
        open_browser : bool (optional)
            if True (default), then open a web browser to the given HTML
        http_server : class (optional)
            optionally specify an HTTPServer class to use for showing the
            figure. The default is Python's basic HTTPServer.
        """
        from ..utils.server import serve
        html = self.to_html(**html_kwargs)
        serve(html, ip=ip, port=port, n_retries=n_retries,
              files=files, jupyter_warning=jupyter_warning,
              open_browser=open_browser, http_server=http_server)

    def _finalize_data(self):
        """
        This function is called by _finalize() below.

        It performs final checks on the data:

        * If the data has too many rows (more than max_rows).
        * Whether the data attribute contains expressions, and if so it extracts
          the appropriate data object and generates the appropriate transforms.
        """
        # Check to see if data has too many rows.
        if isinstance(self.data, pd.DataFrame):
            if len(self.data) > self.max_rows:
                raise MaxRowsExceeded(
                    "Your dataset has too many rows and could take a long "
                    "time to send to the frontend or to render. To override the "
                    "default maximum rows (%s), set the max_rows property of "
                    "your Chart to an integer larger than the number of rows "
                    "in your dataset. Alternatively you could perform aggregations "
                    "or other data reductions before using it with Altair" % DEFAULT_MAX_ROWS
                )

        # Handle expressions.
        if isinstance(self.data, expr.DataFrame):
            columns = self.data._cols
            calculated_cols = self.data._calculated_cols
            filters = self.data._filters
            self.data = self.data._data
            if columns is not None and isinstance(self.data, pd.DataFrame):
                self.data = self.data[columns]
            if calculated_cols:
                self.transform_data(calculate=[CalculateTransform(field, expr=exp)
                                               for field, exp
                                               in calculated_cols.items()])
            if filters:
                filters = [repr(f) for f in filters]
                if len(filters) == 1:
                    self.transform_data(filter=filters[0])
                else:
                    self.transform_data(filter=filters)


class Chart(TopLevelMixin, schema.TopLevelFacetedUnitSpec):
    _data = None

    # use specialized version of Encoding and Transform
    encoding = jst.JSONInstance(Encoding,
                                help=schema.TopLevelFacetedUnitSpec.encoding.help)
    transform = jst.JSONInstance(Transform,
                                 help=schema.TopLevelFacetedUnitSpec.transform.help)
    mark = schema.Mark(default_value='point', help="""The mark type.""")

    max_rows = T.Int(
        default_value=DEFAULT_MAX_ROWS,
        help="Maximum number of rows in the dataset to accept."
    )

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new):
        if isinstance(new, string_types):
            self._data = Data(url=new)
        elif (new is None or isinstance(new, pd.DataFrame)
              or isinstance(new, expr.DataFrame) or isinstance(new, Data)):
            self._data = new
        else:
            raise TypeError('Expected DataFrame or altair.Data, got: {0}'.format(new))

    _skip_on_export = ['data', '_data', 'max_rows']

    def __init__(self, data=None, **kwargs):
        super(Chart, self).__init__(**kwargs)
        self.data = data

    def __dir__(self):
        return [m for m in dir(self.__class__) if m not in dir(T.HasTraits)]

    @use_signature(schema.MarkConfig)
    def mark_area(self, *args, **kwargs):
        """Set the mark to 'area' and optionally specify mark properties"""
        self.mark = 'area'
        return self.configure_mark(*args, **kwargs)

    @use_signature(schema.MarkConfig)
    def mark_bar(self, *args, **kwargs):
        """Set the mark to 'bar' and optionally specify mark properties"""
        self.mark = 'bar'
        return self.configure_mark(*args, **kwargs)

    @use_signature(schema.MarkConfig)
    def mark_errorBar(self, *args, **kwargs):
        """Set the mark to 'errorBar' and optionally specify mark properties"""
        self.mark = 'errorBar'
        return self.configure_mark(*args, **kwargs)

    @use_signature(schema.MarkConfig)
    def mark_line(self, *args, **kwargs):
        """Set the mark to 'line' and optionally specify mark properties"""
        self.mark = 'line'
        return self.configure_mark(*args, **kwargs)

    @use_signature(schema.MarkConfig)
    def mark_point(self, *args, **kwargs):
        """Set the mark to 'point' and optionally specify mark properties"""
        self.mark = 'point'
        return self.configure_mark(*args, **kwargs)

    @use_signature(schema.MarkConfig)
    def mark_rule(self, *args, **kwargs):
        """Set the mark to 'rule' and optionally specify mark properties"""
        self.mark = 'rule'
        return self.configure_mark(*args, **kwargs)

    @use_signature(schema.MarkConfig)
    def mark_text(self, *args, **kwargs):
        """Set the mark to 'text' and optionally specify mark properties"""
        self.mark = 'text'
        return self.configure_mark(*args, **kwargs)

    @use_signature(schema.MarkConfig)
    def mark_tick(self, *args, **kwargs):
        """Set the mark to 'tick' and optionally specify mark properties"""
        self.mark = 'tick'
        return self.configure_mark(*args, **kwargs)

    @use_signature(schema.MarkConfig)
    def mark_circle(self, *args, **kwargs):
        """Set the mark to 'circle' and optionally specify mark properties"""
        self.mark = 'circle'
        return self.configure_mark(*args, **kwargs)

    @use_signature(schema.MarkConfig)
    def mark_square(self, *args, **kwargs):
        """Set the mark to 'square' and optionally specify mark properties"""
        self.mark = 'square'
        return self.configure_mark(*args, **kwargs)

    @use_signature(schema.MarkConfig)
    def configure_mark(self, *args, **kwargs):
        """Configure the chart's marks by keyword args."""
        return update_subtraits(self, ('config', 'mark'), *args, **kwargs)

    @use_signature(schema.Encoding)
    def encode(self, *args, **kwargs):
        """Define the encoding for the Chart."""
        return update_subtraits(self, 'encoding', *args, **kwargs)

    def _finalize(self, **kwargs):
        self._finalize_data()
        # data comes from wrappers, but self.data overrides this if defined
        if self.data is not None:
            kwargs['data'] = self.data
        super(Chart, self)._finalize(**kwargs)

    def __add__(self, other):
        if isinstance(other, Chart):
            lc = LayeredChart()
            lc += self
            lc += other
            return lc
        else:
            raise TypeError('Can only add Charts/LayeredChart to Chart')

    @classmethod
    def from_dict(cls, spec):
        if 'layer' in spec:
            return LayeredChart.from_dict(spec)
        elif 'facet' in spec:
            return FacetedChart.from_dict(spec)
        else:
            return super(Chart, cls).from_dict(spec)

    @classmethod
    def load_example(cls, name):
        """Load an example chart

        Initialize a chart object from one of the built-in examples

        Parameters
        ----------
        example : string
            The example ID or filename, e.g. ``"line"`` or ``"line.json"``

        Returns
        -------
        chart : Chart, LayeredChart, or FacetedChart
            The Chart object containing the example
        """
        from .examples import load_example
        spec = load_example(name)
        return cls.from_dict(spec)


class LayeredChart(TopLevelMixin, schema.TopLevelLayerSpec):
    _data = None

    # Use specialized version of Chart and Transform
    layer = jst.JSONArray(jst.JSONInstance(Chart),
                          help=schema.TopLevelLayerSpec.layer.help)
    transform = jst.JSONInstance(Transform,
                                 help=schema.TopLevelLayerSpec.transform.help)
    max_rows = T.Int(
        default_value=DEFAULT_MAX_ROWS,
        help="Maximum number of rows in the dataset to accept."
    )

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new):
        if isinstance(new, string_types):
            self._data = Data(url=new)
        elif (new is None or isinstance(new, pd.DataFrame)
              or isinstance(new, expr.DataFrame) or isinstance(new, Data)):
            self._data = new
        else:
            raise TypeError('Expected DataFrame or altair.Data, got: {0}'.format(new))

    _skip_on_export = ['data', '_data', 'max_rows']

    def __init__(self, data=None, **kwargs):
        super(LayeredChart, self).__init__(**kwargs)
        self.data = data

    def __dir__(self):
        return [m for m in dir(self.__class__) if m not in dir(T.HasTraits)]

    def set_layers(self, *layers):
        self.layer = list(layers)
        return self

    def _finalize(self, **kwargs):
        self._finalize_data()
        # data comes from wrappers, but self.data overrides this if defined
        if self.data is not None:
            kwargs['data'] = self.data
        super(LayeredChart, self)._finalize(**kwargs)

    def __iadd__(self, layer):
        if self.layer is jst.undefined:
            self.layer = [layer]
        else:
            self.layer = self.layer + [layer]
        return self


class FacetedChart(TopLevelMixin, schema.TopLevelFacetedSpec):
    _data = None

    # Use specialized version of Facet, spec, and Transform
    facet = jst.JSONInstance(Facet, help=schema.TopLevelFacetedSpec.facet.help)
    spec = jst.JSONUnion([jst.JSONInstance(LayeredChart),
                          jst.JSONInstance(Chart)],
                         help=schema.TopLevelFacetedSpec.spec.help)
    transform = jst.JSONInstance(Transform,
                                 help=schema.TopLevelFacetedSpec.transform.help)
    max_rows = T.Int(
        default_value=DEFAULT_MAX_ROWS,
        help="Maximum number of rows in the dataset to accept."
    )

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new):
        if isinstance(new, string_types):
            self._data = Data(url=new)
        elif (new is None or isinstance(new, pd.DataFrame)
              or isinstance(new, expr.DataFrame) or isinstance(new, Data)):
            self._data = new
        else:
            raise TypeError('Expected DataFrame or altair.Data, got: {0}'.format(new))

    _skip_on_export = ['data', '_data', 'max_rows']

    def __init__(self, data=None, **kwargs):
        super(FacetedChart, self).__init__(**kwargs)
        self.data = data

    def __dir__(self):
        return [m for m in dir(self.__class__) if m not in dir(T.HasTraits)]

    @use_signature(schema.Facet)
    def set_facet(self, *args, **kwargs):
        """Define the facet encoding for the Chart."""
        return update_subtraits(self, 'facet', *args, **kwargs)

    def _finalize(self, **kwargs):
        self._finalize_data()
        # data comes from wrappers, but self.data overrides this if defined
        if self.data is not None:
            kwargs['data'] = self.data
        super(FacetedChart, self)._finalize(**kwargs)