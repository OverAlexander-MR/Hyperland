return {
  {
    "mason-org/mason.nvim",
    opts = {
      ensure_installed = {
        "pyright",
        "ruff",
        "black",
      },
    },
  },

  -- LSP de Python
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        -- pyright = {},
      },
    },
  },

  -- Formatters & linters vía none-ls (antes null-ls)
  {
    "nvimtools/none-ls.nvim",
    opts = function(_, opts)
      local nls = require("null-ls")

      opts.sources = opts.sources or {}
      vim.list_extend(opts.sources, {
        nls.builtins.formatting.black,
        -- nls.builtins.diagnostics.ruff,
        -- nls.builtins.formatting.ruff, -- opcional
      })
    end,
  },
}
