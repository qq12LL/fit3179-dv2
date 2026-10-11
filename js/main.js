// Embeds each Vega-Lite spec (stored as a separate, human-readable JSON file in /specs)
// into its placeholder <div>. Shared styling lives in js/vl-config.json.
(async function () {
  const charts = [
    ["#vis01", "specs/01_map_bivariate.vl.json"],
    ["#vis02", "specs/02_heatmap_domains.vl.json"],
    ["#vis03", "specs/03_dumbbell_remoteness.vl.json"],
    ["#vis04", "specs/04_map_schools_strip.vl.json", "canvas", "#vis04-controls"], // ~9,600 points: canvas is faster
    ["#vis05", "specs/05_ridgeline_sector.vl.json"],
    ["#vis06", "specs/06_stacked_sea_sector.vl.json"],
    ["#vis07", "specs/07_map_year12.vl.json"],
    ["#vis08", "specs/08_scatter_irsd_y12.vl.json"],
    ["#vis09", "specs/09_waffle_uni.vl.json"],
    ["#vis10", "specs/10_line_uni_trend.vl.json"],
    ["#vis11", "specs/11_overview_detail_rank.vl.json"],             // overview + detail (brush)
    ["#vis12", "specs/12_small_multiples_years.vl.json", "canvas"]   // small multiples (repeat): 6 maps, canvas is faster
  ];

  let config = {};
  try {
    config = await (await fetch("js/vl-config.json")).json();
  } catch (e) {
    console.warn("Could not load shared chart config", e);
  }

  for (const [el, spec, renderer, bind] of charts) {
    vegaEmbed(el, spec, {
      config,
      bind: bind || undefined, // where to put dropdowns (above the chart)
      renderer: renderer || "svg",
      actions: { export: true, source: false, compiled: false, editor: true },
      tooltip: { theme: "light" }
    }).catch((err) => {
      console.error(spec, err);
      document.querySelector(el).innerHTML =
        '<p class="note">This chart could not be loaded (' + spec + ").</p>";
    });
  }
})();
