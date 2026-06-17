import pyhtml
import subtask1a
import subtask2a
import subtask3a
import subtask_b1
import subtask_b2
import subtask_b3 
# Enable debugging mode to help trace issues
pyhtml.need_debugging_help = True

# Register each page route with its corresponding module
pyhtml.MyRequestHandler.pages["/"] = subtask1a      # Home page (Subtask A1)
pyhtml.MyRequestHandler.pages["/page2"] = subtask2a # Subtask A2
pyhtml.MyRequestHandler.pages["/page3"] = subtask3a # Subtask A3
pyhtml.MyRequestHandler.pages["/page4"] = subtask_b1 #subtask B1
pyhtml.MyRequestHandler.pages["/page5"] = subtask_b2 #subtask B2
pyhtml.MyRequestHandler.pages["/page6"] = subtask_b3 #subtask B3

# Start the local web server
if __name__ == "__main__":
    pyhtml.host_site()
