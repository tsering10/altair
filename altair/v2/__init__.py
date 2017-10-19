from .schema import jstraitlets
undefined = jstraitlets.undefined

from .api import (
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
    Color,
    Column,
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
    ConditionalNumberLegend,
    ConditionalNumberLegendDef,
    ConditionalNumberLegendFieldDef,
    ConditionalNumberLegendValueDef,
    ConditionalStringLegend,
    ConditionalStringLegendDef,
    ConditionalStringLegendFieldDef,
    ConditionalStringLegendValueDef,
    ConditionalText,
    ConditionalTextDef,
    ConditionalTextFieldDef,
    ConditionalTextValueDef,
    Config,
    Data,
    DataFormat,
    DataFormatType,
    DataUrlFormat,
    DateTime,
    Detail,
    ERRORBAR,
    Encoding,
    EncodingWithFacet,
    EqualFilter,
    ExtendedScheme,
    Facet,
    FacetField,
    FacetFieldDef,
    FacetedCompositeUnitSpecAlias,
    FacetedSpec,
    FacetedUnitSpec,
    Field,
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
    Opacity,
    OrFilter,
    Order,
    OrderField,
    OrderFieldDef,
    Orient,
    PositionField,
    PositionFieldDef,
    RangeFilter,
    Repeat,
    RepeatRef,
    RepeatSpec,
    ResolveMapping,
    ResolveMode,
    Row,
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
    Shape,
    SingleDefChannel,
    SingleSelection,
    SingleSelectionConfig,
    Size,
    SortField,
    SpatialResolve,
    Spec,
    StackOffset,
    StringValueDef,
    Summarize,
    SummarizeTransform,
    Text,
    TextConfig,
    TextFieldDef,
    TextValueDef,
    TickConfig,
    TimeUnit,
    TimeUnitTransform,
    Tooltip,
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
    X,
    X2,
    Y,
    Y2,
    MaxRowsExceeded,
    FieldError,
    enable_mime_rendering,
    disable_mime_rendering,
    Chart,
    LayeredChart,
    FacetedChart,
)

from ..datasets import (
    list_datasets,
    load_dataset
)

from ..utils import (
    Vega,
    VegaLite
)

from .. import expr

from ..tutorial import tutorial