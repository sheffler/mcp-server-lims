#
# MCP SERVER LIMS
#   uses FAST MCP server
#   from https://github.com/modelcontextprotocol/python-sdk

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.prompts.base import Message, UserMessage, AssistantMessage

import time
import asyncio
import random

from typing import Generic, List, Optional, TypeVar
from typing import Literal
from pydantic import BaseModel, Field

import sys

#
# LOGGER
#

import logging
logger = logging.getLogger('lims-server')
logger.setLevel(logging.DEBUG)

#
# WORKFLOW PROMPT
#

APROMPT = """

The assistant's goal is to manage the data associated with a set of samples.  There are four steps to track.

1. accessioning - entering the initial samples in the database
2. preparation - calling a tool to process the input samples to attach a tag and monitor a "passed" or "failed" status
3. analysis - calling a tool to analyze the outputs of the preparation step whose status is "passed"
4. report generation - displaying the sample data across the first 3 steps

The assistant's final result should be Workflow Report displayed as a table that shows for each sample:

- the sample name
- the input mass value
- and a column called "Magnitude" with a barchart showing the relative input masses, relative to the maximum mass in the dataset
- the tag value from the preparation step
- the status from the preparation step, show with a colored indicator
- the filename from the analysis step
- the metric from the analysis step



Using my database tool, make sure there is a table named "input_samples" with columns named "sample-name" and "input-mass".  Preload this table with the following data provided from the table below.
<table>
<tr>
  <th>Sample Name</th> <th>Input Mass</th>
<tr>
<tr>
  <td> NA12878 </td> <td> 45 </td>
</tr
<tr>
  <td> NCC1701 </td> <td> 77 </td>
</tr
<tr>
  <td> NACL </td> <td> 12 </td>
</tr
<tr>
  <td> NA12879 </td> <td> 32 </td>
</tr
</table>
"""

#
# The Data Models
#

class InputSample(BaseModel):
    sample_name: str = Field(..., description="sample name identifier")
    mass: int = Field(..., description="sample mass in ng")

class PreparationResult(BaseModel):
    sample_name: str = Field(..., description="sample name identifier")
    tag: str = Field(..., description="identification tag applied to the sample")
    status: Literal['passed', 'failed']
   
class AnalysisResult(BaseModel):
    sample_name: str = Field(..., description="sample name identifier")
    filename: str = Field(..., description="analyzer out file name for this sample")
    metric: float = Field(..., description="the metric calculated as the sample was analyzed")

#
# MCP
#
mcp = FastMCP("Lims Server", debug=True, log_level="DEBUG")

logger.info("LIMS Server HELLO MESSAGE")

#
# ACCESSIONING Prompt
#  After the main prompt, add another one that asks for display of the initial table.
#

@mcp.prompt(name="lims-demo")
def lims_demo() -> list[Message]:
    return [
        UserMessage(APROMPT),
        UserMessage("Can you please show me the sample table?")
    ]


#
# The Preparation Tool
#

tags = [ "actg", "atgg", "accg", "gacc", "tact", "gaca",
         "cgag", "ctct", "gact", "tcga", "ccgg", "tgac",
         "gagg", "gcct"
        ]

@mcp.tool()
async def preparation_tool(sample_list: List[InputSample]) -> List[PreparationResult]:
    """Prepare the samples for analysis.  Mark samples as 'passed' or 'failed'. """

    logger.info(f"PREPARING SAMPLES")

    preparations = [ ]

    for sample in sample_list:
        if random.randint(1, 10) < 8:
            status = "passed"
        else:
            status = "failed"
        

        prep = PreparationResult(
            sample_name = sample.sample_name,
            tag = random.choice(tags),
            status = status)

        logger.info(f"Prepared Sample: {prep}")

        preparations.append(prep)
        await asyncio.sleep(1)

    return preparations


#
# The Analyzer Tool
#


@mcp.tool()
async def analyzer_tool(preparation_list: List[PreparationResult]) -> List[AnalysisResult]:
    """Analyze the samples that have been prepared"""

    logger.info(f"ANALYZING SAMPLES")

    analyses = [ ]

    for sample in preparation_list:

        analysis = AnalysisResult(
            sample_name = sample.sample_name,
            filename = sample.sample_name + "-file.out",
            metric = random.randint(40, 100) / 10.0
            )

        logger.info(f"Analyzed Sample: {analysis}")

        logger.info(f"Analyzed Sample: {analysis}")

        analyses.append(analysis)
        await asyncio.sleep(1)

    return analyses
            


# Entry point to run the server
if __name__ == "__main__":
    mcp.run()

    
