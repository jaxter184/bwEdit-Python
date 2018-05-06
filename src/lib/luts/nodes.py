list = {
	#values
	'float_core.decimal_value_atom(289)': {
		'name':"Decimal Value",
		'i':0,
		'o':1,
	},
	'float_core.boolean_value_atom(87)': {
		'name':"Boolean Value",
		'i':0,
		'o':1,
	},
	'float_core.integer_value_atom(394)': {
		'name':"Integer Value",
		'i':0,
		'o':1,
	},
	'float_core.indexed_value_atom(180)': {
		'name':"Indexed Value",
		'i':0,
		'o':1,
	},
	'float_common_atoms.bipolar_toggleable_decimal_value_atom(1763)': {
		'name':"Decimal Value (toggleable bipolar)",
		'i':0,
		'o':1,
	},
	'float_common_atoms.constant_value_atom(314)': {
		'name':"ConstV",
		'i':0,
		'o':1,
		'w':60,
	},
	'float_common_atoms.constant_integer_value_atom(298)': {
		'name':"ConstI",
		'i':0,
		'o':1,
		'w':60,
	},
	'float_common_atoms.indexed_lookup_table_atom(344)': {
		'name':"LUT",
		'i':[('row index', 2),],
		'o':[('column outputs (array)', 2),],
		'w':60,
	},
	'constant_boolean_value_atom(635)': {
		'name':"ConstB",
		'i':0,
		'o':1,
		'w':60,
	},
	
	#atoms
	'float_common_atoms.nitro_atom(1721)': {
		'name':'Nitro',
		'i':12,
		'o':8,
	},
	'float_common_atoms.mix_atom(301)': {
		'name':"MIX",
		'i':3,
		'o':1,
		'w':30,
		'h':75,
		'vertical':None,
	},
	'float_common_atoms.polyphonic_note_voice_atom(350)': {
		'name':"Polyphonic Note Voice",
		'i':[('Note Event', 1),('Mono', 2),('Legato Glide Enable', 2),('Glide Amount', 3),('Single Trigger Envelope', 2),('Voice Stack', 3),('Voice Limit', 2),('Steal Same Key', 2),],
		'o':[('Note Event', 1),('Pitch', 3),('Velocity', 2),('Gain', 3),('Pan', 3),('presusre?', 3),(),('Pitch (used in sampler)', 3),('Note Event', 1),('Stack Index', 2),],
		'vertical':None,
	},
	'float_common_atoms.monophonic_note_voice_atom(402)': {
		'name':"MonoNoteVoice",
		'i':[('Note Event', 1),],
		'o':[('Note Event', 1),('Pitch', 3),(),('Amp', 3),('Pan', 3),],
		'w':30,
		'vertical':None,
	},
	'float_common_atoms.audio_voice_combiner_atom(313)': {
		'name':"Combine",
		'i':[('Audio In', 3),('Gate', 1),('Steal Release', 3),], #gate might not be an event
		'o':[('Audio Out', 3),],
		'vertical':None,
	},
	'float_common_atoms.delay_compensation_atom(1371)': {
		'name':"DelC",
		'i':1,
		'o':1,
		'w':50,
		'h':50,
	},
	'float_common_atoms.note_delay_compensation_atom(1435)': {
		'name':"Note DelC",
		'i':1,
		'o':1,
		'w':50,
		'h':50,
	},
	'float_common_atoms.processing_delay_placeholder_component(1437)': {
		'name':"Proc DelC",
		'i':1,
		'o':1,
		'w':80,
		'h':50,
	},
	'float_common_atoms.bool_delay_compensation_atom(2017)': {
		'name':"Bool DelC",
		'i':1,
		'o':1,
		'w':80,
		'h':50,
	},
	'note_processing_delay_placeholder_component(2050)': {
		'name':"Note Del",
		'i':2,
		'o':1,
		'w':80,
		'h':50,
	},
	'float_core.modulation_source_atom(766)': {
		'name':"Modulation Source",
		'i':1,
		'o':0,
	},
	'float_core.value_led_atom(189)': {
		'name':"Value LED",
		'i':1,
		'o':0,
		'w':30,
		'h':30,
	},
	'float_core.note_led_atom(558)': {
		'name':"Note LED",
		'i':1,
		'o':0,
		'w':30,
		'h':30,
	},
	'float_core.vu_meter_atom(40)': {
		'name':"VUMeter",
		'i':1,
		'o':0,
		'w':30,
		'vertical':None,
	},
	'float_common_atoms.decimal_event_filter_atom(400)': {
		'name':"DecEvent Filter",
		'i':1,
		'o':1,
		'w':80,
	},
	'float_common_atoms.event_switch_atom(321)': {
		'name':"Event Switch",
		'i':[('Event', 1),('Retrigger', 2),],
		'o':1,
		'w':80,
	},
	'float_common_atoms.select_atom(347)': {
		'name':"SEL",
		'i':3,
		'o':1,
		'w':50,
	},
	'float_common_atoms.multiplexer_atom(1188)': {
		'name':"MUX",
		'i':0,
		'o':1,
		'w':50,
		'h':50,
		'vertical':None,
	},
	'float_common_atoms.stereo_width_atom(297)': {
		'name':"Width",
		'i':2,
		'o':1,
		'w':30,
		'vertical':None,
	},
	'float_core.oscilloscope_atom(1654)': {
		'name':"Dual OScope",
		'i':[('In A',3),('In B',3),('Scale',3),('Gain A',3),('Gain B',3),('Trigger Select',3),('Level',3),('Hold',3),('Trigger Slope Select',3),('Input B Enable',3),('Note Event In',3),],
		'o':1,
		'w':30,
		'vertical':None,
	},
	'float_core.drum_pads(591)': {#draw some stuff
		'name':"DrumPads",
		'i':2,
		'o':1,
		'w':80,
		'center':None,
	},
	'float_core.parallel_nested_device_chain_container(586)': {#draw some stuff
		'name':"Layer",
		'i':2,
		'o':1,
		'w':60,
		'center':None,
	},
	'float_common_atoms.note_range_filter_atom(407)': {
		'name':"Note Filter",
		'i':5,
		'o':1,
		'vertical':None,
	},
	
	#Math
	'float_common_atoms.constant_multiply_atom(303)': {
		'name':"×c",
		'i':1,
		'o':1,
		'w':60,
		'h':50, 
	},
	'float_common_atoms.multiply_add_atom(304)': {
		'name':"×+",
		'i':3,
		'o':1,
		'w':50,
	},
	'float_common_atoms.sum_atom(305)': {
		'name':"++",
		'o':1,
		'w':40,
	},
	'float_common_atoms.constant_add_atom(308)': {
		'name':"+c",
		'i':1,
		'o':1,
		'w':60,
		'h':50, 
	},
	'float_common_atoms.limit_range_atom(311)': {
		'name':"Limit Range",
		'i':3,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.abs_atom(319)': {
		'name':"|x|",
		'i':1,
		'o':1,
		'w':40,
	},
	'float_common_atoms.add_atom(337)': {
		'name':"+",
		'i':2,
		'o':1,
		'w':20,
		'h':50,
	},
	'float_common_atoms.compare_atom(340)': {
		'name':">/</=",
		'i':3,
		'o':1,
		'w':50,
	},
	'float_common_atoms.subtract_atom(343)': {
		'name':"-",
		'i':2,
		'o':1,
		'w':50,
	},
	'float_common_atoms.tanh_atom(345)': {
		'name':"tanh",
		'i':2,
		'o':1,
		'w':50,
	},
	'float_common_atoms.min_atom(348)': {
		'name':"min",
		'i':2,
		'o':1,
		'w':50,
	},
	'float_common_atoms.max_atom(352)': {
		'name':"max",
		'i':2,
		'o':1,
		'w':50,
	},
	'float_common_atoms.and_atom(354)': {
		'name':"&&",
		'i':2,
		'o':1,
		'w':50,
	},
	'float_common_atoms.multiply_atom(367)': {
		'name':"×",
		'i':2,
		'o':1,
		'w':50,
	},
	'float_common_atoms.quantizer_atom(370)': {
		'name':"Quantize",
		'i':[('Audio In', 3),('Level', 3),('not sure', -1),],
		'o':1,
		'vertical':None,
	},
	
	#Control
	'float_common_atoms.analog_adsr_atom(372)': {
		'name':"AnalogADSR",
		'i':[('Pitch', 3),('Attack', 3),('Decay', 3),('Sustain', 3),('Release', 3),],
		'o':[('Amplitude', 3),('unknown', -1),],
		'vertical':None,
	},
	'float_common_atoms.ahdsr_atom(466)': {
		'name':"AHDSR",
		'i':[('Note Event', 1),('Attack Time', 3),('Attack Shape', 3),('Hold Time', 3),('Decay Time', 3),('Decay Shape', 3),('Sustain Level', 3),('Release Time', 3),('Release Shape', 3),],
		'o':[('Amplitude', 3),(),],
		'vertical':None,
	},
	'float_common_atoms.multiphase_lfo_atom(406)': {
		'name':"Multi LFO",
		'i':3,
		'o':2,
		'vertical':None,
	},
	'float_common_atoms.lfo_atom(410)': {
		'name':"LFO",
		'i':[('Rate', 3),('Shape', 3),('Retrig', 1),('Sync', 3),('Phase', 3),('Retrigger Enable', 22),],
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.nameable_modulation_source_atom(1929)': {
		'name':"nameable\no->",
		'i':1,
		'o':0,
		'w':80,
	},
	
	#DSP
	'float_common_atoms.noise_atom(294)': {
		'name':"Noise",
		'i':0,
		'o':[('Audio Out', 3),],
		'vertical':None,
	},
	'float_common_atoms.sample_rate_reduction_atom(295)': {
		'name':"S&H",
		'i':[('Audio In', 3),('Frequency', 3),],
		'o':[('Audio Out', 3),],
		'vertical':None,
	},
	'float_common_atoms.multimode_filter_atom(312)': {
		'name':"Multimode Filter",
		'i':[('Audio In', 3),('Cutoff Frequency', 3),('Resonance', 3),(),(),(),(),(),],
		'o':[('Audio Out', 3),],
		'vertical':None,
	},
	'float_common_atoms.sample_player_atom(330)': {
		'name':"Sampler",
		'i':[('Sampler Resource', -1),('Note Event', 1),('Pitch', 3),('Sample Start', 3),('Loop Start', 3),('Loop Length', 3),],
		'o':[('Audio Out', 3),('Gate', 2),('PolyObs?', 3),('Loop Jump', 1),],
		'vertical':None,
	},
	'float_common_atoms.sine_oscillator_atom(324)': {
		'name':"Sine",
		'i':1,
		'o':[('Audio Out', 3),],
		'w':50,
		'center':None,
	},
	'float_common_atoms.dynamics_gain_computer_atom(335)': {
		'name':"Dynamics Gain Coef",
		'i':7,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.nested_allpass_filter_atom(336)': {
		'name':"AllPass",
		'i':5,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.audio_delay_atom(339)': {
		'name':"Delay",
		'i':4,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.biquad_filter_atom(353)': {
		'name':"BiQ F",
		'i':2,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.allpass_filter_atom(363)': {
		'name':"ALLPASS",
		'i':3,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.biquad_coefficient_atom(365)': {
		'name':"BiQ Coef",
		'i':4,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.mute_atom(395)': {
		'name':"Mute",
		'i':2,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.frequency_shifter_atom(409)': {
		'name':"FreqShift",
		'i':2,
		'o':1,
		'w':80,
		'center':None,
	},
	'float_common_atoms.surge_classic_oscillator_atom(491)': {
		'name':"SURGE",
		'i':[('Pitch', 3),('Shape', 3),('Pulse Width', 3),('Sub Pulse Width', 3),('Sub Level', 3),('Sync', 3),('Unison Spread', 3),('Unison Voices', 3),('who knows', 2),],
		'o':[('Audio Out', 3),],
		'vertical':None,
	},
	'float_common_atoms.feedback_compressor_atom(547)': {
		'name':"Compressor",
		'i':7,
		'o':2,
		'vertical':None,
	},
	'float_common_atoms.fixed_delay_atom(564)': {
		'name':"Fixed Delay",
		'i':1,
		'o':1,
		'w':100,
	},
	'float_common_atoms.limiter_gain_computer_atom(566)': {
		'name':"Lim Gain Coef",
		'i':4,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.svf_filter_atom(578)': {
		'name':"SVF Filter",
		'i':[('Audio In', 3),('Filter Type', 1),('Cutoff Frequency', 3),(),('Resonance', 3),(),],
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.high_cut_atom(600)': {
		'name':"HiCut",
		'i':2,
		'o':1,
		'w':50,
		'center':None,
	},
	'float_common_atoms.phasemod_oscillator_bank_atom(778)': {
		'name':"Phasemod Osc Bank",
		'i':9,
		'o':4,
		'vertical':None,
	},
	'float_common_atoms.note_pitch_atom(1158)': {
		'name':"Note Shift",
		'i':2,
		'o':1,
		'w':90,
		'center':None,
	},
	
	#Components
	'float_core.proxy_in_port_component(154)': {
		'name':"In Port",
		'i':0,
		'o':1,
		'w':50,
		'h':50,
	},
	'float_core.proxy_out_port_component(50)': {
		'name':"Out Port",
		'i':1,
		'o':0,
		'w':50,
		'h':50,
	},
	'float_core.nested_device_chain_slot(587)': {
		'name':"Nest",
		'i':2,
		'o':2,
	},
	'float_core.spectrum_analyser_component(1851)': {
		'name':"Spectrum Analyser",
		'i':1,
		'o':0,
		'w':140,
		'center':None,
	},
	'float_common_atoms.audio_switcher_atom(401)': {
		'name':"AudioSW",
		'i':3,
		'o':1,
		'w':30,
		'vertical':None,
	},
	'float_common_atoms.envelope_follower_atom(300)': {
		'name':"Env Follow",
		'i':3,
		'o':1,
		'w':30,
		'vertical':None,
	},
	'float_core.audio_sidechain_routing_component(857)': {
		'name':"Audio SC",
		'i':1,
		'o':1,
		'w':70,
	},
	'float_core.note_sidechain_routing_component(860)': {
		'name':"Note SC",
		'i':1,
		'o':1,
		'w':70,
	},
	'float_common_atoms.data_array_component(1870)': {
		'name':"Data Array",
		'i':1,
		'o':1,
		'w':80,
	},
	'float_common_atoms.gain_detector_atom(545)': {
		'name':"Gain Detect",
		'i':4,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.domain_converter_atom(320)': {
		'name':"Domain Conv",
		'i':1,
		'o':1,
		'w':75,
	},
	'float_core.gain_change_meter_atom(556)': {
		'name':"Gain Change Meter",
		'i':1,
		'o':0,
		'w':75,
	},
	'float_core.audio_out_routing_component(858)': {
		'name':"Audio Out",
		'i':1,
		'o':1,
		'w':80,
	},
	'float_core.audio_in_routing_component(859)': {
		'name':"Audio In",
		'i':1,
		'o':1,
		'w':80,
	},
	'float_core.midi_out_routing_component(863)': {
		'name':"Midi Out",
		'i':2,
		'o':1,
		'w':80,
	},
	'float_core.midi_in_routing_component(864)': {
		'name':"Midi In",
		'i':2,
		'o':1,
		'w':80,
	},
	'float_common_atoms.user_configurable_processing_delay_placeholder_component(1438)': {
		'name':"User PDC",
		'i':1,
		'o':1,
		'w':80,
	},
	'float_common_atoms.svg_image_component(584)': {
		'name':"SVG",
		'i':0,
		'o':0,
		'w':30,
		'center':None,
	},
	'float_common_atoms.label_component(374)': {
		'name':"LABEL",
		'i':0,
		'o':0,
		'w':60,
	},
	'float_common_atoms.boolean_panel_value(1751)': {
		'name':"BOOLEAN",
		'i':0,
		'o':0,
		'w':60,
	},
	'float_common_atoms.string_panel_value(1754)': {
		'name':"STRING",
		'i':0,
		'o':0,
		'w':60,
	},
	'float_common_atoms.transport_component(1839)': {
		'name':"Transport",
		'i':0,
		'o':9,
		'vertical':None,
	},
	'float_core.trigger_atom(239)': {
		'name':"Trigger",
		'i':0,
		'o':1,
		'w':60,
	},
	'float_common_atoms.note_trigger_atom(1146)': {
		'name':"Note Trigger",
		'i':1,
		'o':1,
		'w':100,
	},
	'float_common_atoms.step_sequencer_atom(1170)': {
		'name':"Step Sequencer",
		'i':5,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.slew_rate_atom(316)': {
		'name':"Slew",
		'i':2,
		'o':1,
		'w':30,
		'vertical':None,
	},
	'float_core.scope_observer_component(1996)': {
		'name':"Scope Obs",
		'i':1,
		'o':0,
		'w':100,
	},
	
	#notes
	'arpeggiator_atom(1232)': {
		'name':"ARP(ugly)",
		'i':40,
		'o':2,
		'vertical':None,
	},
	'float_common_atoms.diatonic_note_transpose_atom(1159)': {
		'name':"Diatonic Transposer",
		'i':11,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.pitch_class_mapping_atom(1153)': {
		'name':"Pitch Mapper",
		'i':15,
		'o':1,
		'vertical':None,
	},
	
	#converters
	'float_common_atoms.interleave_atom(306)': {
		'name':"LR→S",
		'i':2,
		'o':1,
		'w':60,
		'center':None,
	},
	'float_common_atoms.key_to_frequency_atom(317)': {
		'name':"♩→Hz",
		'i':1,
		'o':1,
		'w':60,
		'center':None,
		#"shape":"hex",
	},
	'float_common_atoms.beattime_to_time_atom(327)': {
		'name':"♪→ms",
		'i':1,
		'o':1,
		'w':60,
		'center':None,
		#"shape":"hex",
	},
	'float_common_atoms.deinterleave_atom(368)': {
		'name':"S→LR",
		'i':1,
		'o':2,
		'w':60,
		'center':None,
	},
	'float_common_atoms.int_to_audio_atom(404)': {
		'name':"int→audio",
		'i':1,
		'o':1,
		'w':60,
		'center':None,
		#"shape":"hex",
	},
	'float_common_atoms.int_to_bool_atom(769)': {
		'name':"int→bool",
		'i':1,
		'o':1,
		'w':60,
		'center':None,
		#"shape":"hex",
	},
	'float_common_atoms.note_event_to_decimal_event_atom(787)': {
		'name':"NE→DE",
		'i':2,
		'o':2,
		'w':60,
		'center':None,
		#"shape":"hex",
	},
	
	#misc/unknown
	'float_common_atoms.event_repeater_atom(414)': {
		'name':"E Repeat",
		'i':3,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.velocity_amp_multiplier_atom(471)': {
		'name':"Velocity",
		'i':3,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.held_impulse_atom(405)': {
		'name':"HeldImpulse",
		'i':2,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.exponential_decay_atom(398)': {
		'name':"exp Decay",
		'i':3,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.amp_and_pan_atom(431)': {
		'name':"Amp&Pan",
		'i':[('Audio In', 3),('Amp', 3),('Pan', 3),],
		'o':[('Audio Out', 3),],
		'vertical':None,
	},
	'float_common_atoms.moving_average_filter_atom(565)': {
		'name':"MovingAvg",
		'i':1,
		'o':1,
		'w':60,
	},
	'float_common_atoms.moving_maximum_filter_atom(567)': {
		'name':"MovingMax",
		'i':1,
		'o':1,
		'w':60,
	},
	'float_common_atoms.buffer_reader_atom(331)': {
		'name':"Read",
		'i':1,
		'o':1,
		'w':60,
	},
	'float_common_atoms.buffer_writer_atom(364)': {
		'name':"Write",
		'i':1,
		'o':0,
		'w':60,
	},
	'float_common_atoms.sine_resonator_atom(413)': {
		'name':"SineReso",
		'i':3,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.bend_curve_atom(542)': {
		'name':"BendCurve",
		'i':2,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.vibrato_delaytime_modulation_atom(412)': {
		'name':"D-Vibrato",
		'i':2,
		'o':1,
		'vertical':None,
	},
	'float_core.polyphonic_observer_atom(1815)': {
		'name':"PolyObs",
		'i':2,
		'o':1,
		'vertical':None,
	},
	'last_voice_int_event_atom(2076)': {
		'name':"LVint",
		'i':1,
		'o':1,
		'w':80,
	},
	'last_voice_audio_atom(2077)': {
		'name':"LastVoice",
		'i':1,
		'o':1,
		'w':80,
	},
	'lightweight_oscilloscope_atom(2072)': {
		'name':"OScope",
		'i':4,
		'o':0,
		'vertical':None,
	},
	'int_observer_atom(1234)': {
		'name':"int obs",
		'i':4,
		'o':0,
		'w':80,
	},
	'boolean_observer_atom(2029)': {
		'name':"boolean obs",
		'i':1,
		'o':0,
		'w':120,
	},
	'effect_selector(2067)': {
		'name':"FX Select",
		'i':2,
		'o':1,
		'w':80,
		'center':None,
	},
	'instrument_selector(2068)': {
		'name':"Inst Select",
		'i':2,
		'o':1,
		'w':80,
		'center':None,
	},
	'gate_detector_atom(1235)': {
		'name':"Gate Detect",
		'i':4,
		'o':1,
		'vertical':None,
	},
	'note_generator_atom(1236)': {
		'name':"Note Gen",
		'i':3,
		'o':1,
		'vertical':None,
	},
	'float_common_atoms.sampler_resource_component(529)': {
		'name':"Sampler Resource",
		'i':0,
		'o':1,
		'w':150,
	},
	'float_common_atoms.fft_atom(1847)': {
		'name':"FFT",
		'i':1,
		'o':1,
		'w':50,
		'center':None,
	},
	'float_common_atoms.ifft_atom(1849)': {
		'name':"IFFT",
		'i':1,
		'o':1,
		'w':50,
		'center':None,
	},
	'float_core.spectrum_readout_component(1853)': {
		'name':"IFFT Display",
		'i':1,
		'o':0,
		'w':100,
		'center':None,
	},
}
