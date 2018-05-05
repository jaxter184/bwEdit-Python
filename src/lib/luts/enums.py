units = [
	"none",
	"percent",
	"dB",
	"seconds",
	"Hz", #log scale
	"not sure", #0 converts to -36.376, slope = 2
	"octave",
	"BPM", #log scale
	"also not sure",
	"cents" #slope = 200
	"semitones", #slope = 2
	"ratio", #0 = 1:inf
	"inverse ratio",
	"0 converts to 127", #seems to be vaguely exponential
	"meters", #0 = 1m, .477 = 3m, -1.477 = .033m
	"degrees",
]

domains = [
	"Linear",
	"dB",
	"(log10(1/A13)+1)*40-3.5",
	"log(x)",
	"1/x",
	"10^(log(x)/3)",
	"2*dB",
]

usesEnums = {"unit(296)":units, "domain(294)":domains, "engine_domain(295)":domains, "source_domain(727)":domains, "destination_domain(728)":domains,}