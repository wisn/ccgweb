<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:import href="cat.xsl"/>
	<xsl:param name="standalone" select="'no'"/>
	<xsl:output method="html" encoding="UTF-8"/>
	<xsl:template match="/">
		<xsl:choose>
			<xsl:when test="$standalone = 'yes'">
				<xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;</xsl:text>
				<html lang="en">
					<head>
						<title>Derivations</title>
						<link rel="stylesheet" type="text/css" href="css/der.css"/>
					</head>
					<body>
						<main>
							<xsl:apply-templates/>
						</main>
					</body>
				</html>
			</xsl:when>
			<xsl:otherwise>
				<xsl:apply-templates/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template match="lexlist">
		<xsl:element name="div">
			<xsl:attribute name="class">lexlist</xsl:attribute>
			<td>
				<xsl:apply-templates />
			</td>
		</xsl:element>
	</xsl:template>
	<xsl:template match="der">
		<div class="der">
			<xsl:apply-templates/>
		</div>
	</xsl:template>
	<xsl:template match="lex">
		<xsl:element name="table">
			<xsl:attribute name="class">constituent lex</xsl:attribute>
			<xsl:attribute name="data-token">
				<xsl:value-of select="token"/>
			</xsl:attribute>
			<xsl:attribute name="data-from">
				<xsl:value-of select="tag[@type='from']"/>
			</xsl:attribute>
			<xsl:attribute name="data-to">
				<xsl:value-of select="tag[@type='to']"/>
			</xsl:attribute>
			<xsl:if test="cat">
				<xsl:attribute name="data-cat">
					<xsl:apply-templates select="cat"/>
				</xsl:attribute>
			</xsl:if>
			<tr>
				<td class="token">
					<xsl:value-of select="token"/>
				</td>
			</tr>
			<tr>
				<td class="cat" tabindex="0">
					<xsl:choose>
						<xsl:when test="cat">
							<xsl:apply-templates select="cat"/>
						</xsl:when>
						<xsl:when test="tag[@type = 'super']">
							<xsl:apply-templates select="tag[@type = 'super']"/>
						</xsl:when>
						<xsl:otherwise>&#160;</xsl:otherwise>
					</xsl:choose>
				</td>
			</tr>
			<xsl:if test="not(tag[@type='to'] = '-1')">
				<tr>
					<td class="span-swiper">&#160;</td>
				</tr>
			</xsl:if>
		</xsl:element>
	</xsl:template>
	<xsl:template match="unaryrule">
		<xsl:element name="table" class="constituent unaryrule">
			<xsl:attribute name="class">constituent unaryrule</xsl:attribute>
			<xsl:attribute name="data-cat">
				<xsl:apply-templates select="cat"/>
			</xsl:attribute>
			<tr class="daughters">
				<td class="daughter daughter-only">
					<xsl:apply-templates select="(binaryrule|unaryrule|lex)[1]"/>
				</td>
			</tr>
			<tr>
				<td class="rulecat">
					<div class="rulecat">
						<xsl:element name="div">
							<xsl:attribute name="class">cat</xsl:attribute>
							<xsl:apply-templates select="cat"/>
						</xsl:element>
						<xsl:element name="div">
							<xsl:attribute name="class">rule</xsl:attribute>
							<xsl:attribute name="title"><xsl:value-of select="@description"/></xsl:attribute>
							<xsl:choose>
								<xsl:when test="@type = 'ftr'">
									T&#8239;<sup>&gt;</sup>
								</xsl:when>
								<xsl:when test="@type = 'btr'">
									T&#8239;<sup>&lt;</sup>
								</xsl:when>
								<xsl:otherwise>
									*
								</xsl:otherwise>
							</xsl:choose>
						</xsl:element>
					</div>
				</td>
			</tr>
		</xsl:element>
	</xsl:template>
	<xsl:template match="binaryrule[name((binaryrule|unaryrule|lex)[1]) = 'lex' and lex[1]/token/text() = 'ø']">
		<xsl:element name="table">
			<xsl:attribute name="class">constituent unaryrule</xsl:attribute>
			<xsl:attribute name="data-cat">
				<xsl:apply-templates select="cat"/>
			</xsl:attribute>
			<tr class="daughters">
				<td class="daughter daughter-only">
					<xsl:apply-templates select="(binaryrule|unaryrule|lex)[2]"/>
				</td>
			</tr>
			<tr>
				<td class="rulecat">
					<div class="rulecat">
						<xsl:element name="div">
							<xsl:attribute name="class">cat</xsl:attribute>
							<xsl:apply-templates select="cat"/>
						</xsl:element>
						<xsl:element name="div">
							<xsl:attribute name="class">rule</xsl:attribute>
							<xsl:attribute name="title">Type Changing</xsl:attribute>
							*
						</xsl:element>
					</div>
				</td>
			</tr>
		</xsl:element>
	</xsl:template>
	<xsl:template match="binaryrule">
		<xsl:element name="table">
			<xsl:attribute name="class">constituent binaryrule</xsl:attribute>
			<xsl:attribute name="data-cat">
				<xsl:apply-templates select="cat"/>
			</xsl:attribute>
			<tr class="daughters">
				<td class="daughter daughter-left">
					<xsl:apply-templates select="(binaryrule|unaryrule|lex)[1]"/>
				</td>
				<td class="daughter daughter-right">
					<xsl:apply-templates select="(binaryrule|unaryrule|lex)[2]"/>
				</td>
			</tr>
			<tr>
				<td colspan="2" class="rulecat">
					<div class="rulecat">
						<xsl:element name="div">
							<xsl:attribute name="class">cat</xsl:attribute>
							<xsl:apply-templates select="cat"/>
						</xsl:element>
						<xsl:element name="div">
							<xsl:attribute name="class">rule</xsl:attribute>
							<xsl:attribute name="title"><xsl:value-of select="@description"/></xsl:attribute>
							<xsl:choose>
								<xsl:when test="@type='fa'">&gt;&#8239;<sup>0</sup></xsl:when>
								<xsl:when test="@type='fc'">&gt;&#8239;<sup>1</sup></xsl:when>
								<xsl:when test="@type='gfc'">&gt;&#8239;<sup><i>n</i></sup></xsl:when>
								<xsl:when test="@type='gbc'">&lt;&#8239;<sup><i>n</i></sup></xsl:when>
								<xsl:when test="@type='bc'">&lt;&#8239;<sup>1</sup></xsl:when>
								<xsl:when test="@type='conj'">∨</xsl:when>
								<xsl:when test="@type='bxc'">&lt;&#8239;<sup>1</sup><sub>×</sub></xsl:when>
								<xsl:when test="@type='fxc'">&gt;&#8239;<sup>1</sup><sub>×</sub></xsl:when>
								<xsl:when test="@type='gbxc'">&lt;&#8239;<sup><i>n</i></sup><sub>×</sub></xsl:when>
								<xsl:when test="@type='gfxc'">&gt;&#8239;<sup><i>n</i></sup></xsl:when>
								<xsl:when test="@type='ba'">&lt;&#8239;<sup>0</sup></xsl:when>
								<xsl:when test="@type='rp'">.</xsl:when>
								<xsl:when test="@type='lp'">.</xsl:when>
							</xsl:choose>
						</xsl:element>
					</div>
				</td>
			</tr>
		</xsl:element>
	</xsl:template>
</xsl:stylesheet>
