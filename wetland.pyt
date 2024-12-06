import arcpy

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Wetland Analysis Toolbox"
        self.alias = "wetlandanalysis"
        self.tools = [WetlandsNearParks]

class WetlandsNearParks(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Wetlands Near National Parks"
        self.description = "Identifies wetlands within a specified distance of national parks."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []

        parks_fc = arcpy.Parameter(
            displayName="National Parks Feature Class",
            name="parks_fc",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        params.append(parks_fc)

        wetlands_fc = arcpy.Parameter(
            displayName="Wetlands Feature Class",
            name="wetlands_fc",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        params.append(wetlands_fc)

        buffer_distance = arcpy.Parameter(
            displayName="Buffer Distance",
            name="buffer_distance",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        buffer_distance.value = "20000 Meters"  # Default value
        params.append(buffer_distance)

        output_fc = arcpy.Parameter(
            displayName="Output Feature Class",
            name="output_fc",
            datatype="DEFeatureClass",
            parameterType="Derived",
            direction="Output")
        params.append(output_fc)

        province = arcpy.Parameter(
            displayName="Province Code (Optional)",
            name="province",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        params.append(province)

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        try:
            # Get parameter values
            parks_fc = parameters[0].valueAsText
            wetlands_fc = parameters[1].valueAsText
            buffer_distance = parameters[2].valueAsText
            output_fc = parameters[3].valueAsText
            province = parameters[4].valueAsText if parameters[4].altered else None

            # Set workspace
            arcpy.env.workspace = arcpy.env.scratchGDB

            # Select national parks (optionally by province)
            if province:
                parks_layer = self.select_parks_by_province(parks_fc, province)
            else:
                parks_layer = arcpy.management.MakeFeatureLayer(parks_fc, "parks_layer")

            # Create a buffer around selected parks
            buffer_layer = self.create_park_buffer(parks_layer, buffer_distance)

            # Select wetlands within the buffer
            wetlands_layer = arcpy.management.MakeFeatureLayer(wetlands_fc, "wetlands_layer")
            self.select_wetlands_in_buffer(wetlands_layer, buffer_layer)

            # Export selected wetlands to a new feature class
            self.export_selected_features(wetlands_layer, output_fc)

            arcpy.AddMessage("Analysis complete. Output saved to: " + output_fc)
        except arcpy.ExecuteError:
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            arcpy.AddError(str(e))

    def select_parks_by_province(self, parks_fc, province_code):
        parks_layer = arcpy.management.MakeFeatureLayer(parks_fc, "parks_layer")
        arcpy.management.SelectLayerByAttribute(parks_layer, "NEW_SELECTION", f"CPC_CODE = '{province_code}'")
        return parks_layer

    def create_park_buffer(self, parks_layer, buffer_distance):
        buffer_fc = "in_memory/park_buffer"
        arcpy.analysis.Buffer(parks_layer, buffer_fc, buffer_distance)
        buffer_layer = arcpy.management.MakeFeatureLayer(buffer_fc, "buffer_layer")
        return buffer_layer
